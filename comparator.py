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

class MovieComparator:
    def __init__(self, llm_client: LLMClient, db: Database, enriched_movies_path: str = "data/enriched_movies.csv"):
        self.llm = llm_client
        self.db = db
        try:
            self.enriched_df = pd.read_csv(enriched_movies_path)
        except:
            self.enriched_df = None
    
    def compare(self, movie_ids: List[int]) -> Dict:
        movies_data = []
        movies_df = self.db.fetch_movies_by_ids(movie_ids)
        
        for movie_id in movie_ids:
            movie_info = movies_df[movies_df['movieId'] == movie_id]
            if not movie_info.empty:
                movie_dict = movie_info.iloc[0].to_dict()
                avg_rating = self.db.get_movie_avg_rating(movie_id)
                
                enriched_info = {}
                if self.enriched_df is not None:
                    enriched_row = self.enriched_df[self.enriched_df['movieId'] == movie_id]
                    if not enriched_row.empty:
                        enriched_info = {
                            'sentiment': enriched_row.iloc[0].get('sentiment'),
                            'budget_tier': enriched_row.iloc[0].get('budget_tier'),
                            'revenue_tier': enriched_row.iloc[0].get('revenue_tier'),
                            'production_effectiveness': enriched_row.iloc[0].get('production_effectiveness')
                        }
                
                movie_dict.update({
                    'average_rating': avg_rating,
                    **enriched_info
                })
                movies_data.append(movie_dict)
        
        if not movies_data:
            return {"error": "No movies found for comparison"}
        
        prompt = Prompts.build_comparison_prompt(movies_data)
        system_msg = Prompts.get_comparison_system_message()
        
        try:
            response = self.llm.generate(prompt, system_msg, json_mode=True)
            return json.loads(response)
        except Exception as e:
            print(f"Error generating comparison: {e}")
            return {"error": str(e)}

