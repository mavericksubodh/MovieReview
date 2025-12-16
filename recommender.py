import pandas as pd
from database import get_db_connection
from llm_client import LLMClient
from prompts import Prompts

class Recommender:
    def __init__(self):
        self.llm_client = LLMClient()
        self.prompts = Prompts()
        self.db_conn = get_db_connection()

    def get_enriched_movies(self):
        """Fetches all enriched movies from the database."""
        try:
            df = pd.read_sql_query("SELECT * FROM movies_enriched", self.db_conn)
            return df
        except pd.io.sql.DatabaseError:
            print("Error: 'movies_enriched' table not found. Please run the 'enrich' command first.")
            return pd.DataFrame()

    def recommend(self, query):
        """Generates movie recommendations based on a user query."""
        enriched_movies = self.get_enriched_movies()
        if enriched_movies.empty:
            return "No enriched movie data available to generate recommendations."

        movies_data = enriched_movies.to_dict('records')
        
        prompt = self.prompts.build_recommendation_prompt(query, movies_data)
        system_message = self.prompts.get_recommendation_system_message()
        
        recommendations = self.llm_client.generate(prompt, system_message, json_mode=True)
        return recommendations

if __name__ == '__main__':
    # Example usage:
    recommender = Recommender()
    test_query = "Recommend some high-revenue action movies with positive sentiment."
    recommendations = recommender.recommend(test_query)
    print(f"Recommendations for query: '{test_query}'")
    print(recommendations)
