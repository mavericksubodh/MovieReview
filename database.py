import sqlite3
import pandas as pd

# Swapped paths to match the actual table contents
MOVIES_DB_PATH = 'db/movies_attributes_v2.db'
RATINGS_DB_PATH = 'db/ratings.db'

def get_db_connection(db_path):
    """Establishes a connection to a specified SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_movie_sample(sample_size=50):
    """Fetches a random sample of movies from the database."""
    conn = get_db_connection(MOVIES_DB_PATH)
    query = "SELECT * FROM movies ORDER BY RANDOM() LIMIT ?"
    df = pd.read_sql_query(query, conn, params=(sample_size,))
    conn.close()
    return df

def save_enriched_data(df, table_name='movies_enriched'):
    """Saves the enriched movie data to a new table in the movies database."""
    # The enriched data will be saved in the main movies.db file (which is ratings.db)
    conn = get_db_connection(MOVIES_DB_PATH)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print(f"Data saved to table: {table_name} in {MOVIES_DB_PATH}")

def get_movie_avg_rating(movie_id: int) -> float:
    """Fetches the average rating for a given movie from the ratings database."""
    conn = get_db_connection(RATINGS_DB_PATH)
    query = "SELECT AVG(rating) as avg_rating FROM ratings WHERE movieId = ?"
    cursor = conn.cursor()
    result = cursor.execute(query, (movie_id,)).fetchone()
    conn.close()
    if result and result['avg_rating'] is not None:
        return result['avg_rating']
    return 0.0

if __name__ == '__main__':
    # Example usage:
    sample_df = get_movie_sample(5)
    print("Fetched movie sample:")
    print(sample_df.head())
    if not sample_df.empty:
        test_movie_id = sample_df.iloc[0]['movieId']
        avg_rating = get_movie_avg_rating(test_movie_id)
        print(f"Average rating for movie {test_movie_id}: {avg_rating}")
