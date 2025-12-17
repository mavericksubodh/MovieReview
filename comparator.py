import pandas as pd
from llm_client import LLMClient
from prompts import Prompts
# Import the specific path and the connection function
from database import get_db_connection, MOVIES_DB_PATH

class Comparator:
    def __init__(self):
        self.llm_client = LLMClient()
        self.prompts = Prompts()

    def get_movie_details(self, movie_ids):
        """Fetches details for a list of movies from the movies database."""
        if not movie_ids:
            return pd.DataFrame()
        
        conn = get_db_connection(MOVIES_DB_PATH)
        # The movie_ids list needs to be converted to a tuple for the query
        query = f"SELECT * FROM movies WHERE movieId IN ({','.join(['?']*len(movie_ids))})"
        df = pd.read_sql_query(query, conn, params=tuple(movie_ids))
        conn.close()
        return df

    def compare(self, movie_ids):
        """Generates a comparison of two or more movies."""
        if len(movie_ids) < 2:
            return "Please provide at least two movie IDs to compare."

        movie_details = self.get_movie_details(movie_ids)
        if len(movie_details) < len(movie_ids):
            found_ids = movie_details['movieId'].tolist()
            missing_ids = set(movie_ids) - set(found_ids)
            return f"Could not find movie details for all provided IDs. Missing: {missing_ids}"

        movies_data = movie_details.to_dict('records')

        prompt = self.prompts.build_comparison_prompt(movies_data)
        system_message = self.prompts.get_comparison_system_message()

        comparison = self.llm_client.generate(prompt, system_message, json_mode=True)
        return comparison

if __name__ == '__main__':
    # Example usage:
    comparator = Comparator()
    # Replace with actual movie IDs from your database
    test_movie_ids = [1, 2] 
    comparison = comparator.compare(test_movie_ids)
    print(f"Comparison for movie IDs: {test_movie_ids}")
    print(comparison)
