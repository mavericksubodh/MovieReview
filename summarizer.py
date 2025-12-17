import pandas as pd
from llm_client import LLMClient
from prompts import Prompts
# Import the specific paths and the connection function
from database import get_db_connection, MOVIES_DB_PATH, RATINGS_DB_PATH

class Summarizer:
    def __init__(self):
        self.llm_client = LLMClient()
        self.prompts = Prompts()

    def get_user_ratings(self, user_id):
        """Fetches a user's rating history from the ratings database."""
        conn = get_db_connection(RATINGS_DB_PATH)
        query = "SELECT * FROM ratings WHERE userId = ?"
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        return df

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

    def summarize(self, user_id):
        """Generates a summary of a user's preferences."""
        user_ratings = self.get_user_ratings(user_id)
        if user_ratings.empty:
            return f"No ratings found for user ID: {user_id}"

        # Get all movie IDs from ratings
        movie_ids = user_ratings['movieId'].tolist()
        total_ratings = len(movie_ids)
        
        # Get movie details for those movie IDs
        movie_details = self.get_movie_details(movie_ids)
        
        # Get the set of movie IDs that have details
        movies_with_details = set(movie_details['movieId'].tolist()) if not movie_details.empty else set()
        
        # Filter ratings to only include movies that have details
        filtered_ratings = user_ratings[user_ratings['movieId'].isin(movies_with_details)]
        
        # Calculate missing movies
        missing_movie_ids = set(movie_ids) - movies_with_details
        ratings_with_details = len(filtered_ratings)
        
        # Warn about missing movies
        if missing_movie_ids:
            print(f"Warning: {len(missing_movie_ids)} rating(s) excluded due to missing movie details (movieIds: {sorted(missing_movie_ids)})")
        
        if filtered_ratings.empty:
            return f"No ratings found with corresponding movie details for user ID: {user_id}"
        
        # Inform user about filtering
        if ratings_with_details < total_ratings:
            print(f"Analyzing {ratings_with_details} out of {total_ratings} ratings (movies with available details)")
        else:
            print(f"Analyzing all {ratings_with_details} ratings")
        
        # Convert to dictionaries for prompt
        ratings_data = filtered_ratings.to_dict('records')
        movie_details_data = movie_details.to_dict('records')
        
        # Ensure ratings and movie details are properly matched
        # Create a mapping of movieId to movie details for quick lookup
        movie_details_dict = {movie['movieId']: movie for movie in movie_details_data}
        
        # Verify all ratings have corresponding movie details
        verified_ratings = []
        for rating in ratings_data:
            movie_id = rating['movieId']
            if movie_id in movie_details_dict:
                verified_ratings.append(rating)
        
        if not verified_ratings:
            return f"No valid ratings with movie details found for user ID: {user_id}"
        
        prompt = self.prompts.build_summary_prompt(user_id, verified_ratings, movie_details_data)
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
