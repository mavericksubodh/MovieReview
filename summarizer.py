import pandas as pd
from database import get_db_connection
from llm_client import LLMClient
from prompts import Prompts

class Summarizer:
    def __init__(self):
        self.llm_client = LLMClient()
        self.prompts = Prompts()
        self.db_conn = get_db_connection()

    def get_user_ratings(self, user_id):
        """Fetches a user's rating history."""
        query = "SELECT * FROM ratings WHERE userId = ?"
        df = pd.read_sql_query(query, self.db_conn, params=(user_id,))
        return df

    def get_movie_details(self, movie_ids):
        """Fetches details for a list of movies."""
        if not movie_ids:
            return pd.DataFrame()
        
        query = f"SELECT * FROM movies WHERE movieId IN ({','.join(['?']*len(movie_ids))})"
        df = pd.read_sql_query(query, self.db_conn, params=movie_ids)
        return df

    def summarize(self, user_id):
        """Generates a summary of a user's preferences."""
        user_ratings = self.get_user_ratings(user_id)
        if user_ratings.empty:
            return f"No ratings found for user ID: {user_id}"

        movie_ids = user_ratings['movieId'].tolist()
        movie_details = self.get_movie_details(movie_ids)

        ratings_data = user_ratings.to_dict('records')
        movie_details_data = movie_details.to_dict('records')

        prompt = self.prompts.build_summary_prompt(user_id, ratings_data, movie_details_data)
        system_message = self.prompts.get_summary_system_message()

        summary = self.llm_client.generate(prompt, system_message, json_mode=True)
        return summary

if __name__ == '__main__':
    # Example usage:
    summarizer = Summarizer()
    test_user_id = 1
    summary = summarizer.summarize(test_user_id)
    print(f"Preference summary for user ID: {test_user_id}")
    print(summary)
