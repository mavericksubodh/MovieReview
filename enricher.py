import json
import pandas as pd
from typing import Dict, List
from llm_client import LLMClient
from prompts import Prompts
import database as db

class MovieEnricher:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def _get_avg_ratings_for_batch(self, movie_ids: List[int]) -> Dict[int, float]:
        """Fetches average ratings for a batch of movie IDs in a single query."""
        conn = db.get_db_connection(db.RATINGS_DB_PATH)
        query = f"""
            SELECT movieId, AVG(rating) as avg_rating
            FROM ratings
            WHERE movieId IN ({','.join(['?']*len(movie_ids))})
            GROUP BY movieId;
        """
        df = pd.read_sql_query(query, conn, params=tuple(movie_ids))
        conn.close()
        # Create a dictionary for quick lookups: {movieId: avg_rating}
        return pd.Series(df.avg_rating.values, index=df.movieId).to_dict()

    def enrich_batch(self, movies_batch: List[Dict]) -> List[Dict]:
        """
        Enriches a single batch of movie dictionaries using the LLM.
        Returns a list of enriched movie dictionaries.
        """
        if not movies_batch:
            return []

        batch_movie_ids = [m['movieId'] for m in movies_batch]
        
        # Get average ratings for the current batch
        avg_ratings = self._get_avg_ratings_for_batch(batch_movie_ids)
        
        # Add the average rating to each movie dictionary in the batch
        for movie in movies_batch:
            movie['avg_rating'] = avg_ratings.get(movie['movieId'], 0.0)

        # Build the batch prompt
        prompt = Prompts.build_batch_enrichment_prompt(movies_batch)
        system_msg = Prompts.get_batch_enrichment_system_message()
        
        try:
            # Make a single API call for the entire batch
            response = self.llm.generate(prompt, system_msg, json_mode=True)
            batch_enriched_data = json.loads(response).get("enriched_movies", [])
            
            # The LLM should return one enriched object for each movie, in order.
            # We'll add the original movieId back to each enriched object.
            for original_movie, enriched_result in zip(movies_batch, batch_enriched_data):
                enriched_result['movieId'] = original_movie['movieId']
            
            return batch_enriched_data
            
        except Exception as e:
            print(f"Error processing batch: {e}")
            # Return default error data for each movie in the batch
            error_data = []
            for movie in movies_batch:
                error_data.append({"movieId": movie['movieId'], "sentiment": "error", "budget_tier": "error", "revenue_tier": "error", "production_effectiveness": "error", "age_category": "error"})
            return error_data
