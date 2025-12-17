import json
import pandas as pd
from typing import Dict, List, Optional
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
                error_data.append({
                    "movieId": movie['movieId'], 
                    "sentiment": "error", 
                    "budget_tier": "error", 
                    "revenue_tier": "error", 
                    "production_effectiveness": "error", 
                    "age_category": "error"
                })
            return error_data

    def enrich_movies(self, movies_df: pd.DataFrame, batch_size: int = 10) -> pd.DataFrame:
        """
        Enrich a DataFrame of movies by processing them in batches.
        
        Args:
            movies_df: DataFrame containing movie data to enrich
            batch_size: Number of movies to process in each batch
            
        Returns:
            DataFrame with enriched movie data
        """
        if movies_df.empty:
            return pd.DataFrame()
        
        # Convert DataFrame to list of dictionaries
        movies_list = movies_df.to_dict('records')
        
        all_enriched = []
        
        # Process in batches
        for i in range(0, len(movies_list), batch_size):
            batch = movies_list[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1} ({len(batch)} movies)...")
            enriched_batch = self.enrich_batch(batch)
            all_enriched.extend(enriched_batch)
        
        # Convert back to DataFrame
        enriched_df = pd.DataFrame(all_enriched)
        return enriched_df

    def enrich(
        self, 
        movie_id: Optional[int] = None,
        size: Optional[int] = None,
        process_all: bool = False,
        batch_size: int = 10,
        skip_existing: bool = True
    ) -> pd.DataFrame:

        # Validate arguments
        if sum([movie_id is not None, size is not None, process_all]) != 1:
            raise ValueError("Exactly one of movie_id, size, or process_all must be specified")
        
        # 1. Get the list of movies to potentially process
        if movie_id is not None:
            print(f"Fetching specific movie with ID: {movie_id}...")
            movies_df = db.get_movie_by_id(movie_id)
        elif process_all:
            print("Fetching all movies from the database...")
            movies_df = db.get_all_movies()
        else:
            # Default to size if not specified
            size = size or 50
            print(f"Fetching a random sample of {size} movies...")
            movies_df = db.get_movie_sample(size)
        
        if movies_df.empty:
            print("No movies found to process.")
            return pd.DataFrame()

        # 2. Filter out already enriched movies if requested
        if skip_existing:
            print("Checking for already enriched movies to avoid re-processing...")
            existing_ids = db.get_existing_enriched_movie_ids()
            
            original_count = len(movies_df)
            movies_to_process_df = movies_df[~movies_df['movieId'].isin(existing_ids)]
            new_count = len(movies_to_process_df)
            
            print(f"Found {original_count} movies. After filtering, there are {new_count} new movies to enrich.")
            
            if movies_to_process_df.empty:
                print("All selected movies have already been enriched. Nothing to do.")
                return pd.DataFrame()
            
            movies_df = movies_to_process_df

        # 3. Enrich the movies
        print(f"Enriching {len(movies_df)} movie(s)...")
        enriched_df = self.enrich_movies(movies_df, batch_size=batch_size)
        
        # 4. Save to database if we have results
        if not enriched_df.empty:
            print("Saving new enriched data to the database...")
            db.save_enriched_data(enriched_df)
            print(f"Data enrichment complete. Enriched {len(enriched_df)} movie(s).")
        else:
            print("Enrichment process did not return any data to save.")
        
        return enriched_df
