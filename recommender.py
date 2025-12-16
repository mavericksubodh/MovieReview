import pandas as pd
from llm_client import LLMClient
from prompts import Prompts
# Import the specific path and the connection function
from database import get_db_connection, MOVIES_DB_PATH

class Recommender:
    def __init__(self):
        self.llm_client = LLMClient()
        self.prompts = Prompts()
    
    def get_enriched_movies(self):
        """
        Fetches all enriched movies and JOINS them with the original movie
        data to create a complete dataset for the LLM.
        """
        conn = get_db_connection(MOVIES_DB_PATH)
        
        # This JOIN query is the key to fixing the recommendation logic.
        query = """
            SELECT
                m.movieId,
                m.title,
                m.overview,
                m.genres,
                me.sentiment,
                me.budget_tier,
                me.revenue_tier,
                me.production_effectiveness,
                me.age_category
            FROM
                movies AS m
            JOIN
                movies_enriched AS me ON m.movieId = me.movieId;
        """
        
        try:
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except pd.io.sql.DatabaseError:
            conn.close()
            print("Error: 'movies_enriched' table not found or query failed. Please run the 'enrich' command first.")
            return pd.DataFrame()

    def recommend(self, query):
        """Generates movie recommendations based on a user query."""
        # Now this function gets the complete, joined data.
        enriched_movies = self.get_enriched_movies()
        if enriched_movies.empty:
            return "No enriched movie data available to generate recommendations."

        # To avoid overwhelming the LLM, let's use a sample of the enriched data
        if len(enriched_movies) > 200:
            enriched_movies = enriched_movies.sample(n=200, random_state=1) # Using random_state for reproducibility

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
