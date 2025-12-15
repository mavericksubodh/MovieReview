import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

class MovieRecommender:
    """
    A class to handle movie recommendations using a FAISS index and movie metadata.
    """
    def __init__(self, index_path='movie_index.faiss', metadata_path='movie_metadata.json'):
        """
        Initializes the recommender by loading the FAISS index, metadata, and the model.
        """
        print("Loading resources for the movie recommender...")
        try:
            self.index = faiss.read_index(index_path)
            
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
            
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Recommender loaded successfully.")
            
        except FileNotFoundError as e:
            print(f"Error: {e}. Please ensure you have run 'create_embeddings.py' to generate the index and metadata files.")
            raise
        except Exception as e:
            print(f"An error occurred during initialization: {e}")
            raise

    def recommend(self, query, top_k=5, min_runtime=None, max_runtime=None, genres=None, release_era=None, min_budget=None, min_revenue=None, audience=None):
        """
        Finds the top_k most relevant movies for a given query, with optional filtering.
        """
        if not hasattr(self, 'model'):
            print("Recommender is not initialized. Cannot perform recommendation.")
            return []

        print(f"\nSearching for movies matching query: '{query}'")
        
        query_embedding = self.model.encode([query], convert_to_tensor=False)
        
        num_candidates = top_k * 50
        distances, indices = self.index.search(np.array(query_embedding), num_candidates)
        
        results = []
        for i in indices[0]:
            movie = self.metadata[i]
            
            # --- Apply Filters ---
            if min_runtime is not None and (movie.get('runtime') is None or movie['runtime'] < min_runtime):
                continue
            if max_runtime is not None and (movie.get('runtime') is None or movie['runtime'] > max_runtime):
                continue
            if min_budget is not None and (movie.get('budget') is None or movie['budget'] < min_budget):
                continue
            if min_revenue is not None and (movie.get('revenue') is None or movie['revenue'] < min_revenue):
                continue
            if release_era is not None and movie.get('releaseEra', '').lower() != release_era.lower():
                continue
            if audience is not None and movie.get('Audience', '').lower() != audience.lower():
                continue
            
            if genres is not None:
                try:
                    movie_genres_list = json.loads(movie.get('genres', '[]'))
                    if not isinstance(movie_genres_list, list):
                        continue
                    
                    genre_names = {g['name'].lower() for g in movie_genres_list if 'name' in g}
                    requested_genres = {g.lower() for g in genres}
                    
                    if not requested_genres.intersection(genre_names):
                        continue
                except (json.JSONDecodeError, TypeError):
                    continue

            results.append(movie)
            
            if len(results) == top_k:
                break
        
        if len(results) < top_k:
            print(f"  Warning: Found only {len(results)} of the requested {top_k} movies that match all criteria.")
                
        return results

# Example of how to use the recommender
if __name__ == '__main__':
    try:
        recommender = MovieRecommender()
        
        # --- Example Query 1: Simple semantic search ---
        print("\n--- 1. Simple Query ---")
        recommendations_1 = recommender.recommend("a movie about a robot who falls in love", top_k=2)
        for movie in recommendations_1:
            print(f"  Title: {movie['title']} (Runtime: {movie.get('runtime', 'N/A')} mins)")

        # --- Example Query 2: Search with a runtime filter ---
        print("\n--- 2. Query with Runtime Filter ---")
        recommendations_2 = recommender.recommend("an epic journey in a fantasy world", top_k=2, min_runtime=150)
        for movie in recommendations_2:
            print(f"  Title: {movie['title']} (Runtime: {movie.get('runtime', 'N/A')} mins)")

        # --- Example Query 3: Complex query with realistic filters ---
        print("\n--- 3. Complex Query with Realistic Filters ---")
        complex_query = "A mind-bending science fiction movie about dreams, reality, or time travel"
        
        recommendations_3 = recommender.recommend(
            complex_query, 
            top_k=3, 
            genres=["Science Fiction"], 
            release_era="Modern" # Adjusted to match the data
        )
        
        if recommendations_3:
            for movie in recommendations_3:
                print(f"  Title: {movie['title']} (Era: {movie.get('releaseEra')}, Genres: {movie.get('genres')})")
        else:
            print("  No movies found matching the specific criteria.")

    except Exception as e:
        print(f"Failed to run recommendation example: {e}")
