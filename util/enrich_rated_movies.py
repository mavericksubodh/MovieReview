import sys
import os
import pandas as pd
import time # Import time for delays

# This allows the script to find and import modules from the project's root directory.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    from database import (
        get_db_connection,
        MOVIES_DB_PATH,
        RATINGS_DB_PATH,
        get_existing_enriched_movie_ids,
        save_enriched_data
    )
    from enricher import MovieEnricher
    from llm_client import LLMClient
except ImportError as e:
    print("Error: Could not import necessary modules.")
    print(f"Please ensure this script is located in the 'util' folder of your project.")
    print(f"Details: {e}")
    sys.exit(1)

def get_rated_movie_ids() -> list[int]:
    """Fetches a distinct list of all movie IDs from the ratings table."""
    print(f"Connecting to ratings database: {RATINGS_DB_PATH}")
    conn = get_db_connection(RATINGS_DB_PATH)
    try:
        df = pd.read_sql_query("SELECT DISTINCT movieId FROM ratings", conn)
        conn.close()
        print(f"Found {len(df)} movies with ratings.")
        return df['movieId'].tolist()
    except Exception as e:
        print(f"Error fetching rated movie IDs: {e}")
        conn.close()
        return []

def get_movies_by_ids(movie_ids: list[int]) -> pd.DataFrame:
    """Fetches full movie details for a given list of movie IDs."""
    if not movie_ids:
        return pd.DataFrame()
    print(f"Connecting to movies database to fetch details for {len(movie_ids)} movies...")
    conn = get_db_connection(MOVIES_DB_PATH)
    all_movies_df = pd.DataFrame()
    # Fetch in chunks to avoid exceeding SQL variable limits
    chunk_size = 900 # SQLite has a limit on the number of variables in an IN clause
    for i in range(0, len(movie_ids), chunk_size):
        chunk_ids = movie_ids[i:i + chunk_size]
        query = f"SELECT * FROM movies WHERE movieId IN ({','.join(['?']*len(chunk_ids))})"
        chunk_df = pd.read_sql_query(query, conn, params=tuple(chunk_ids))
        all_movies_df = pd.concat([all_movies_df, chunk_df], ignore_index=True)
    conn.close()
    return all_movies_df

def main():
    """Main function to run the standalone enrichment script with progressive saving."""
    print("--- Standalone Enrichment Script for Rated Movies (Progressive Saving) ---")
    
    # 1. Get all movie IDs that have ratings
    rated_ids = get_rated_movie_ids()
    if not rated_ids:
        print("No rated movies found. Exiting.")
        return

    # 2. Get the list of movies that are ALREADY enriched
    print("Checking for already enriched movies to avoid re-processing...")
    existing_ids = get_existing_enriched_movie_ids()
    
    # 3. Find the new movies to process
    new_movie_ids = list(set(rated_ids) - set(existing_ids))
    
    print(f"Found {len(rated_ids)} rated movies. {len(existing_ids)} are already enriched.")
    print(f"There are {len(new_movie_ids)} new movies to process.")

    if not new_movie_ids:
        print("All rated movies have already been enriched. Nothing to do.")
        return

    # 4. Fetch the full details for the new movies
    movies_to_process_df = get_movies_by_ids(new_movie_ids)
    
    if movies_to_process_df.empty:
        print("Could not fetch details for the new movies. Exiting.")
        return

    # Convert DataFrame to a list of dictionaries for easier batching
    movies_to_process_list = movies_to_process_df.to_dict('records')

    # 5. Initialize LLM client and movie enricher
    print("Initializing LLM client and movie enricher...")
    llm_client = LLMClient()
    enricher = MovieEnricher(llm_client)
    
    # 6. Process movies in batches and save progressively
    batch_size = 20 # Same batch size as used in enricher
    total_movies = len(movies_to_process_list)
    
    print(f"Starting enrichment of {total_movies} movies in batches of {batch_size}...")
    
    for i in range(0, total_movies, batch_size):
        batch = movies_to_process_list[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_movies + batch_size - 1) // batch_size # Ceiling division
        
        print(f"\nProcessing batch {batch_num}/{total_batches} ({len(batch)} movies)...")
        
        try:
            enriched_batch_data = enricher.enrich_batch(batch)
            
            if enriched_batch_data:
                enriched_batch_df = pd.DataFrame(enriched_batch_data)
                save_enriched_data(enriched_batch_df) # Save this batch immediately
                print(f"Successfully enriched and saved batch {batch_num}.")
            else:
                print(f"Batch {batch_num} returned no enriched data.")
                
        except Exception as e:
            print(f"Error processing batch {batch_num}: {e}")
            print("Skipping this batch and continuing with the next.")
        
        # Optional: Add a small delay between batches to avoid hitting API rate limits
        time.sleep(1) 

    print("\n--- All requested rated movies processed! ---")

if __name__ == "__main__":
    main()
