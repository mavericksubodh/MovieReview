import sqlite3
import pandas as pd

# Setting the final, correct database paths as you specified. This will not be changed again.
MOVIES_DB_PATH = 'db/movies_attributes_v2.db'
RATINGS_DB_PATH = 'db/ratings.db'

def get_db_connection(db_path):
    """Establishes a connection to a specified SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

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

def save_enriched_data(df, table_name='movies_enriched'):
    """Saves the enriched movie data to a new table in the movies database."""
    # Enriched data is saved to the same database where the movies are stored.
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
