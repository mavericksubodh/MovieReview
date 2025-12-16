import json
import pandas as pd
from typing import Dict
from llm_client import LLMClient
from prompts import Prompts
import database as db

class MovieEnricher:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    def enrich_movie(self, movie: Dict) -> Dict:
        movie_id = movie.get('movieId')
        avg_rating = db.get_movie_avg_rating(movie_id)
        
        prompt = Prompts.build_enrichment_prompt(movie, avg_rating)
        system_msg = Prompts.get_enrichment_system_message()
        
        try:
            response = self.llm.generate(prompt, system_msg, json_mode=True)
            enriched = json.loads(response)
            enriched['movieId'] = movie_id
            
            # Print the enriched output for review
            print("--- Enriched Data ---")
            print(json.dumps(enriched, indent=2))
            print("-----------------------")
            
            return enriched
        except Exception as e:
            print(f"Error enriching movie {movie_id}: {e}")
            return {
                "movieId": movie_id,
                "sentiment": "neutral",
                "budget_tier": "medium",
                "revenue_tier": "medium",
                "production_effectiveness": "medium",
                "age_category": "adult"
            }
    
    def enrich_movies(self, movies_df: pd.DataFrame) -> pd.DataFrame:
        enriched_list = []
        
        for idx, row in movies_df.iterrows():
            movie_dict = row.to_dict()
            print(f"\nEnriching {idx+1}/{len(movies_df)}: {movie_dict.get('title')}")
            enriched_data = self.enrich_movie(movie_dict)
            enriched_list.append(enriched_data)
        
        return pd.DataFrame(enriched_list)
