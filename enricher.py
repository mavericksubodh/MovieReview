import json
import pandas as pd
from typing import List, Dict
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

    def enrich_movies(self, movies_df: pd.DataFrame, batch_size: int = 20) -> pd.DataFrame:
        """
        Enriches a DataFrame of movies in batches to improve efficiency.
        """
        all_enriched_data = []
        
        # Convert DataFrame to a list of dictionaries for easier processing
        movies_to_process = movies_df.to_dict('records')
        
        for i in range(0, len(movies_to_process), batch_size):
            batch = movies_to_process[i:i + batch_size]
            batch_movie_ids = [m['movieId'] for m in batch]
            
            print(f"Processing batch {(i // batch_size) + 1}/{(len(movies_to_process) // batch_size) + 1}...")
            
            # Get average ratings for the current batch
            avg_ratings = self._get_avg_ratings_for_batch(batch_movie_ids)
            
            # Add the average rating to each movie dictionary in the batch
            for movie in batch:
                movie['avg_rating'] = avg_ratings.get(movie['movieId'], 0.0)

            # Build the batch prompt
            prompt = Prompts.build_batch_enrichment_prompt(batch)
            system_msg = Prompts.get_batch_enrichment_system_message()
            
            try:
                # Make a single API call for the entire batch
                response = self.llm.generate(prompt, system_msg, json_mode=True)
                batch_enriched_data = json.loads(response).get("enriched_movies", [])
                
                # The LLM should return one enriched object for each movie, in order.
                # We'll add the original movieId back to each enriched object.
                for original_movie, enriched_result in zip(batch, batch_enriched_data):
                    enriched_result['movieId'] = original_movie['movieId']
                
                all_enriched_data.extend(batch_enriched_data)
                
            except Exception as e:
                print(f"Error processing batch starting at index {i}: {e}")
                # As a fallback, you could add default error data for each movie in the batch
                for movie in batch:
                    all_enriched_data.append({"movieId": movie['movieId'], "error": "failed_to_enrich"})

        return pd.DataFrame(all_enriched_data)
