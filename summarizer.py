import json
from typing import Dict, List

try:
    from .llm_client import LLMClient
    from .db import Database
    from .prompts import Prompts
except ImportError:
    from llm_client import LLMClient
    from db import Database
    from prompts import Prompts

class UserPreferenceSummarizer:
    def __init__(self, llm_client: LLMClient, db: Database):
        self.llm = llm_client
        self.db = db
    
    def summarize(self, user_id: int) -> Dict:
        ratings_df = self.db.fetch_user_ratings(user_id)
        if ratings_df.empty:
            return {"error": f"No ratings found for user {user_id}"}
        
        ratings_data = []
        movie_ids = ratings_df['movieId'].tolist()
        movies_df = self.db.fetch_movies_by_ids(movie_ids)
        
        for _, rating_row in ratings_df.iterrows():
            movie_id = rating_row['movieId']
            movie_info = movies_df[movies_df['movieId'] == movie_id]
            if not movie_info.empty:
                movie_dict = movie_info.iloc[0].to_dict()
                ratings_data.append({
                    "movieId": movie_id,
                    "title": movie_dict.get('title'),
                    "rating": float(rating_row['rating']),
                    "overview": movie_dict.get('overview'),
                    "genres": movie_dict.get('genres'),
                    "budget": movie_dict.get('budget'),
                    "revenue": movie_dict.get('revenue')
                })
        
        movie_details = [r for r in ratings_data]
        
        prompt = Prompts.build_summary_prompt(user_id, ratings_data, movie_details)
        system_msg = Prompts.get_summary_system_message()
        
        try:
            response = self.llm.generate(prompt, system_msg, json_mode=True)
            return json.loads(response)
        except Exception as e:
            print(f"Error generating summary: {e}")
            return {"error": str(e)}

