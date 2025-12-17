import sqlite3
import pandas as pd
from typing import List

# Setting the final, correct database paths.
MOVIES_DB_PATH = 'db/movies_attributes_v2.db'
RATINGS_DB_PATH = 'db/ratings.db'

def get_db_connection(db_path):
    """Establishes a connection to a specified SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_movie_by_id(movie_id: int):
    """Fetches a single movie by its ID."""
    conn = get_db_connection(MOVIES_DB_PATH)
    query = "SELECT * FROM movies WHERE movieId = ?"
    df = pd.read_sql_query(query, conn, params=(movie_id,))
    conn.close()
    return df

def get_movie_sample(sample_size=50):
    """Fetches a random sample of movies from the movies database."""
    conn = get_db_connection(MOVIES_DB_PATH)
    query = "SELECT * FROM movies ORDER BY RANDOM() LIMIT ?"
    df = pd.read_sql_query(query, conn, params=(sample_size,))
    conn.close()
    return df

def get_all_movies():
    """Fetches all movies from the movies database."""
    conn = get_db_connection(MOVIES_DB_PATH)
    query = "SELECT * FROM movies"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_existing_enriched_movie_ids() -> List[int]:
    """
    Fetches the IDs of all movies that are already present in the
    movies_enriched table to avoid reprocessing them.
    """
    conn = get_db_connection(MOVIES_DB_PATH)
    try:
        # Check if the table exists first
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='movies_enriched';")
        if cursor.fetchone() is None:
            conn.close()
            return [] # Return empty list if table doesn't exist

        # If table exists, fetch the movieIds
        df = pd.read_sql_query("SELECT movieId FROM movies_enriched", conn)
        conn.close()
        return df['movieId'].tolist()
    except Exception as e:
        print(f"Error fetching existing enriched IDs: {e}")
        conn.close()
        return []

def save_enriched_data(df, table_name='movies_enriched'):
    """
    Saves the enriched movie data to a new table using 'append' mode.
    This adds new data without destroying existing data.
    """
    conn = get_db_connection(MOVIES_DB_PATH)
    df.to_sql(table_name, conn, if_exists='append', index=False)
    conn.close()
    print(f"Appended {len(df)} new records to table: {table_name} in {MOVIES_DB_PATH}")

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
