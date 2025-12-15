import sqlite3
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import json
import os
import time

def create_movie_embeddings():
    """
    Reads movie data from the database, creates embeddings, 
    and saves them to a FAISS index and a corresponding metadata file.
    Skips generation if the embeddings are already up-to-date.
    """
    db_path = 'db/movies_attributes_v2.db'
    index_path = 'movie_index.faiss'
    metadata_path = 'movie_metadata.json'

    # --- Check if embeddings need to be updated ---
    if os.path.exists(index_path) and os.path.exists(metadata_path) and os.path.exists(db_path):
        db_mod_time = os.path.getmtime(db_path)
        index_mod_time = os.path.getmtime(index_path)
        
        if index_mod_time > db_mod_time:
            print("Embeddings are already up-to-date. Skipping generation.")
            return

    print("Change detected in database or embeddings are missing. Generating new embeddings...")
    try:
        # Connect to the database
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row  # This allows accessing columns by name
            cursor = conn.cursor()

            # Fetch all movies with all their attributes
            cursor.execute("SELECT * FROM movies")
            movies = cursor.fetchall()

            if not movies:
                print("No movies found in the database.")
                return

            print(f"Found {len(movies)} movies.")

            movie_texts = []
            # We will now create a list of dictionaries to hold all movie metadata
            movie_metadata = []

            for movie in movies:
                # Combine text fields for semantic embedding
                overview = movie['overview'] if movie['overview'] else ""
                genres = movie['genres'] if movie['genres'] else ""
                combined_text = f"Title: {movie['title']}. Overview: {overview}. Genres: {genres}"
                movie_texts.append(combined_text)
                
                # Store all movie attributes in our metadata list.
                # We'll use the index in the list as the identifier that links to FAISS.
                movie_metadata.append(dict(movie))

            # Load the sentence-transformer model
            print("Loading sentence-transformer model...")
            model = SentenceTransformer('all-MiniLM-L6-v2')

            # Generate embeddings
            print("Generating embeddings for all movies. This may take a while...")
            embeddings = model.encode(movie_texts, convert_to_tensor=False)
            print(f"Embeddings generated with shape: {embeddings.shape}")

            # Create and build the FAISS index
            embedding_dimension = model.get_sentence_embedding_dimension()
            index = faiss.IndexFlatL2(embedding_dimension)
            index.add(np.array(embeddings))

            # Save the FAISS index
            print("Saving FAISS index...")
            faiss.write_index(index, index_path)
            
            # Save the comprehensive metadata file
            print("Saving movie metadata...")
            with open(metadata_path, 'w') as f:
                json.dump(movie_metadata, f, indent=4)

            print("Embeddings and metadata created and saved successfully!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    create_movie_embeddings()
