import argparse
import json
import sys
import os

try:
    from .db import Database
    from .llm_client import LLMClient
    from .enricher import MovieEnricher
    from .recommender import MovieRecommender
    from .summarizer import UserPreferenceSummarizer
    from .comparator import MovieComparator
except ImportError:
    from db import Database
    from llm_client import LLMClient
    from enricher import MovieEnricher
    from recommender import MovieRecommender
    from summarizer import UserPreferenceSummarizer
    from comparator import MovieComparator

def enrich_command(args):
    db = Database()
    llm = LLMClient()
    enricher = MovieEnricher(llm, db)
    
    movies_df = db.fetch_movies(limit=args.limit, offset=0)
    print(f"Enriching {len(movies_df)} movies...")
    enricher.enrich_movies(movies_df, args.output)

def recommend_command(args):
    db = Database()
    llm = LLMClient()
    recommender = MovieRecommender(llm, args.enriched)
    
    movies_df = db.fetch_movies(limit=1000)
    recommender.load_movie_details(movies_df)
    
    query = args.query or "Recommend action movies with high revenue and positive sentiment"
    recommendations = recommender.recommend(query, args.top_k)
    
    print(f"\nRecommendations for: {query}\n")
    print(json.dumps(recommendations, indent=2))

def summarize_command(args):
    db = Database()
    llm = LLMClient()
    summarizer = UserPreferenceSummarizer(llm, db)
    
    summary = summarizer.summarize(args.user_id)
    print(f"\nUser Preference Summary for User {args.user_id}:\n")
    print(json.dumps(summary, indent=2))

def compare_command(args):
    db = Database()
    llm = LLMClient()
    comparator = MovieComparator(llm, db, args.enriched)
    
    movie_ids = [int(x.strip()) for x in args.movie_ids.split(',')]
    comparison = comparator.compare(movie_ids)
    
    print(f"\nMovie Comparison:\n")
    print(json.dumps(comparison, indent=2))

def main():
    parser = argparse.ArgumentParser(description='Movie Review System')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    enrich_parser = subparsers.add_parser('enrich', help='Enrich movies with LLM')
    enrich_parser.add_argument('--limit', type=int, default=80, help='Number of movies to enrich')
    enrich_parser.add_argument('--output', type=str, default='data/enriched_movies.csv', help='Output CSV path')
    
    recommend_parser = subparsers.add_parser('recommend', help='Get movie recommendations')
    recommend_parser.add_argument('--query', type=str, help='Recommendation query')
    recommend_parser.add_argument('--top-k', type=int, default=5, help='Number of recommendations')
    recommend_parser.add_argument('--enriched', type=str, default='data/enriched_movies.csv', help='Enriched movies CSV')
    
    summarize_parser = subparsers.add_parser('summarize-user', help='Summarize user preferences')
    summarize_parser.add_argument('--user-id', type=int, required=True, help='User ID')
    
    compare_parser = subparsers.add_parser('compare', help='Compare movies')
    compare_parser.add_argument('--movie-ids', type=str, required=True, help='Comma-separated movie IDs')
    compare_parser.add_argument('--enriched', type=str, default='data/enriched_movies.csv', help='Enriched movies CSV')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'enrich':
        enrich_command(args)
    elif args.command == 'recommend':
        recommend_command(args)
    elif args.command == 'summarize-user':
        summarize_command(args)
    elif args.command == 'compare':
        compare_command(args)

if __name__ == '__main__':
    main()

