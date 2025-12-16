import sqlite3
import pandas as pd
from typing import List, Dict, Optional

class Database:
    def __init__(self, movies_db_path: str = "db/movies.db", ratings_db_path: str = "db/ratings.db"):
        self.movies_db = movies_db_path
        self.ratings_db = ratings_db_path
    
    def get_connection(self, db_path: str):
        return sqlite3.connect(db_path)
    
    def fetch_movies(self, limit: int = 100, offset: int = 0) -> pd.DataFrame:
        conn = self.get_connection(self.movies_db)
        query = f"SELECT * FROM movies LIMIT {limit} OFFSET {offset}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def fetch_movie_by_id(self, movie_id: int) -> Optional[Dict]:
        conn = self.get_connection(self.movies_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movies WHERE movieId = ?", (movie_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            cols = [desc[0] for desc in cursor.description]
            return dict(zip(cols, row))
        return None
    
    def fetch_movies_by_ids(self, movie_ids: List[int]) -> pd.DataFrame:
        conn = self.get_connection(self.movies_db)
        placeholders = ','.join(['?'] * len(movie_ids))
        query = f"SELECT * FROM movies WHERE movieId IN ({placeholders})"
        df = pd.read_sql_query(query, conn, params=movie_ids)
        conn.close()
        return df
    
    def fetch_user_ratings(self, user_id: int) -> pd.DataFrame:
        conn = self.get_connection(self.ratings_db)
        query = "SELECT * FROM ratings WHERE userId = ?"
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        return df
    
    def get_movie_avg_rating(self, movie_id: int) -> float:
        conn = self.get_connection(self.ratings_db)
        cursor = conn.cursor()
        cursor.execute("SELECT AVG(rating) FROM ratings WHERE movieId = ?", (movie_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result[0] else 0.0
    
    def get_all_movie_ratings(self) -> pd.DataFrame:
        conn = self.get_connection(self.ratings_db)
        df = pd.read_sql_query("SELECT movieId, AVG(rating) as avg_rating, COUNT(*) as rating_count FROM ratings GROUP BY movieId", conn)
        conn.close()
        return df

