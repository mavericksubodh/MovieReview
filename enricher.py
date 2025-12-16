import json
import pandas as pd
from typing import List, Dict

try:
    from .llm_client import LLMClient
    from .db import Database
    from .prompts import Prompts
except ImportError:
    from llm_client import LLMClient
    from db import Database
    from prompts import Prompts

class MovieEnricher:
    def __init__(self, llm_client: LLMClient, db: Database):
        self.llm = llm_client
        self.db = db
    
    def enrich_movie(self, movie: Dict) -> Dict:
        movie_id = movie.get('movieId')
        avg_rating = self.db.get_movie_avg_rating(movie_id)
        
        prompt = Prompts.build_enrichment_prompt(movie, avg_rating)
        system_msg = Prompts.get_enrichment_system_message()
        
        try:
            response = self.llm.generate(prompt, system_msg, json_mode=True)
            enriched = json.loads(response)
            enriched['movieId'] = movie_id
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
    
    def enrich_movies(self, movies_df: pd.DataFrame, output_path: str = "data/enriched_movies.csv"):
        enriched_list = []
        
        for idx, row in movies_df.iterrows():
            movie_dict = row.to_dict()
            enriched = self.enrich_movie(movie_dict)
            enriched_list.append(enriched)
            print(f"Enriched {idx+1}/{len(movies_df)}: {movie_dict.get('title')}")
        
        enriched_df = pd.DataFrame(enriched_list)
        enriched_df.to_csv(output_path, index=False)
        print(f"Saved enriched data to {output_path}")
        return enriched_df

