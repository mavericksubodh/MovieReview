import json
import pandas as pd
from typing import List, Dict

try:
    from .llm_client import LLMClient
    from .prompts import Prompts
except ImportError:
    from llm_client import LLMClient
    from prompts import Prompts

class MovieRecommender:
    def __init__(self, llm_client: LLMClient, enriched_movies_path: str = "data/enriched_movies.csv"):
        self.llm = llm_client
        self.enriched_df = pd.read_csv(enriched_movies_path)
    
    def load_movie_details(self, movies_df: pd.DataFrame):
        self.movies_df = movies_df
    
    def recommend(self, query: str, top_k: int = 5) -> List[Dict]:
        movies_data = []
        for _, row in self.enriched_df.iterrows():
            movie_id = row['movieId']
            movie_info = self.movies_df[self.movies_df['movieId'] == movie_id]
            if not movie_info.empty:
                movie_dict = movie_info.iloc[0].to_dict()
                movie_dict.update({
                    'sentiment': row.get('sentiment'),
                    'budget_tier': row.get('budget_tier'),
                    'revenue_tier': row.get('revenue_tier'),
                    'production_effectiveness': row.get('production_effectiveness'),
                    'age_category': row.get('age_category')
                })
                movies_data.append(movie_dict)
        
        prompt = Prompts.build_recommendation_prompt(query, movies_data)
        system_msg = Prompts.get_recommendation_system_message()
        
        try:
            response = self.llm.generate(prompt, system_msg, json_mode=True)
            result = json.loads(response)
            return result.get('recommendations', [])[:top_k]
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []

