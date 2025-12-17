import argparse
import pandas as pd
# Import the new get_existing_enriched_movie_ids function
from database import get_movie_sample, save_enriched_data, get_all_movies, get_movie_by_id, get_existing_enriched_movie_ids
from enricher import MovieEnricher
from llm_client import LLMClient
from recommender import Recommender
from summarizer import Summarizer
from comparator import Comparator

def enrich_data(size, process_all, movie_id):
    """Enrich movie data intelligently, avoiding re-processing."""
    print("Initializing LLM client and movie enricher...")
    llm_client = LLMClient()
    enricher = MovieEnricher(llm_client)

    enricher.enrich(
        movie_id=movie_id,
        size=size if not process_all and not movie_id else None,
        process_all=process_all
    )
def recommend_movies(query):
    """Get movie recommendations based on a query."""
    print(f"Getting recommendations for query: '{query}'")
    recommender = Recommender()
    recommendations = recommender.recommend(query)
    print("Recommendations:")
    print(recommendations)

def summarize_user(user_id):
    """Summarize a user's preferences."""
    print(f"Summarizing preferences for user ID: {user_id}")
    summarizer = Summarizer()
    summary = summarizer.summarize(user_id)
    print("User Preference Summary:")
    print(summary)

def compare_movies(movie_ids):
    """Compare two or more movies."""
    print(f"Comparing movies with IDs: {movie_ids}")
    comparator = Comparator()
    comparison = comparator.compare(movie_ids)
    print("Movie Comparison:")
    print(comparison)

def main():
    parser = argparse.ArgumentParser(description="Movie System CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Enrich data command
    enrich_parser = subparsers.add_parser("enrich", help="Enrich movie data")
    enrich_parser.add_argument("--size", type=int, default=50, help="Number of movies to enrich")
    enrich_parser.add_argument("--all", action="store_true", help="Process all movies in the database")
    enrich_parser.add_argument("--movie_id", type=int, help="Process a single specific movie by its ID")

    # Recommend movies command
    recommend_parser = subparsers.add_parser("recommend", help="Get movie recommendations")
    recommend_parser.add_argument("query", type=str, help="Recommendation query")

    # Summarize user command
    summarize_parser = subparsers.add_parser("summarize", help="Summarize user preferences")
    summarize_parser.add_argument("user_id", type=int, help="User ID")

    # Compare movies command
    compare_parser = subparsers.add_parser("compare", help="Compare movies")
    compare_parser.add_argument("movie_ids", type=int, nargs="+", help="List of movie IDs to compare")

    args = parser.parse_args()

    if args.command == "enrich":
        enrich_data(args.size, args.all, args.movie_id)
    elif args.command == "recommend":
        recommend_movies(args.query)
    elif args.command == "summarize":
        summarize_user(args.user_id)
    elif args.command == "compare":
        compare_movies(args.movie_ids)

if __name__ == "__main__":
    main()
