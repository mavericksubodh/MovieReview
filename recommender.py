import pandas as pd
from llm_client import LLMClient
from prompts import Prompts
# Import the specific path and the connection function
from database import get_db_connection, MOVIES_DB_PATH

class Recommender:
    def __init__(self):
        self.llm_client = LLMClient()
        self.prompts = Prompts()
        # No longer storing a single connection object
    
    def get_enriched_movies(self):
        """Fetches all enriched movies from the database."""
        # Establish a connection here, for this specific task
        conn = get_db_connection(MOVIES_DB_PATH)
        try:
            df = pd.read_sql_query("SELECT * FROM movies_enriched", conn)
            conn.close()
            return df
        except pd.io.sql.DatabaseError:
            conn.close()
            print("Error: 'movies_enriched' table not found. Please run the 'enrich' command first.")
            return pd.DataFrame()

    def recommend(self, query):
        """Generates movie recommendations based on a user query."""
        enriched_movies = self.get_enriched_movies()
        if enriched_movies.empty:
            return "No enriched movie data available to generate recommendations."

        # To avoid overwhelming the LLM, let's use a sample of the enriched data
        if len(enriched_movies) > 200:
            enriched_movies = enriched_movies.sample(n=200)

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
