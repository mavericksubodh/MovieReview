import json
from typing import List, Dict

class Prompts:
    @staticmethod
    def get_enrichment_system_message() -> str:
        return "You are a movie data analyst. Always return valid JSON only."
    
    @staticmethod
    def build_enrichment_prompt(movie: Dict, avg_rating: float) -> str:
        return f"""Analyze this movie and generate 5 attributes in JSON format:

Movie Title: {movie.get('title', 'N/A')}
Overview: {movie.get('overview', 'N/A')}
Budget: ${movie.get('budget', 0):,}
Revenue: ${movie.get('revenue', 0):,}
Average Rating: {avg_rating:.2f}
Runtime: {movie.get('runtime', 0)} minutes
Genres: {movie.get('genres', 'N/A')}

Generate these attributes:
1. sentiment: positive/neutral/negative (based on overview tone)
2. budget_tier: low/medium/high (reason about industry standards)
3. revenue_tier: low/medium/high (reason about box office performance)
4. production_effectiveness: low/medium/high (analyze rating, budget-to-revenue ratio, and overall success)
5. age_category: kid/teen/adult (based on content and themes)

Return ONLY valid JSON:
{{
  "sentiment": "positive|neutral|negative",
  "budget_tier": "low|medium|high",
  "revenue_tier": "low|medium|high",
  "production_effectiveness": "low|medium|high",
  "age_category": "kid|teen|adult"
}}"""
    
    @staticmethod
    def get_recommendation_system_message() -> str:
        return "You are a movie recommendation expert. Return valid JSON with movie recommendations."
    
    @staticmethod
    def build_recommendation_prompt(query: str, movies_data: List[Dict]) -> str:
        movies_json = json.dumps(movies_data, indent=2)
        return f"""Given this enriched movie dataset, generate personalized recommendations.

User Query: {query}

Movie Dataset:
{movies_json}

Analyze the dataset and recommend 5 movies that best match the user's criteria.
For each recommendation, provide:
- movieId
- title
- reasoning: why this movie matches the query
- key_matching_attributes: which attributes from the query this movie satisfies

Return JSON format:
{{
  "recommendations": [
    {{
      "movieId": 123,
      "title": "Movie Title",
      "reasoning": "explanation",
      "key_matching_attributes": ["attribute1", "attribute2"]
    }}
  ]
}}"""
    
    @staticmethod
    def get_summary_system_message() -> str:
        return "You are a user preference analyst. Return valid JSON with preference analysis."
    
    @staticmethod
    def build_summary_prompt(user_id: int, ratings_data: List[Dict], movie_details: List[Dict]) -> str:
        ratings_summary = json.dumps(ratings_data, indent=2)
        movies_summary = json.dumps(movie_details, indent=2)
        return f"""Analyze this user's movie rating history and preferences.

User ID: {user_id}

User's Ratings:
{ratings_summary}

Movie Details for Rated Movies:
{movies_summary}

Generate:
1. preference_summary: Natural language summary of user's preferences (genres, themes, movie types they like)
2. top_preferred_genres: List of genres the user prefers most
3. average_rating_tendency: Whether they rate high/low/neutral on average
4. recommended_movies: Suggest 3-5 movies they might like based on their preferences (provide movieId and title)

Return JSON:
{{
  "preference_summary": "detailed text summary",
  "top_preferred_genres": ["genre1", "genre2"],
  "average_rating_tendency": "high|medium|low",
  "recommended_movies": [
    {{"movieId": 123, "title": "Movie Title", "reasoning": "why recommended"}}
  ]
}}"""
    
    @staticmethod
    def get_comparison_system_message() -> str:
        return "You are a movie analyst. Return valid JSON with detailed movie comparisons."
    
    @staticmethod
    def build_comparison_prompt(movies_data: List[Dict]) -> str:
        movies_json = json.dumps(movies_data, indent=2)
        return f"""Compare these movies across multiple dimensions.

Movies to Compare:
{movies_json}

Generate a comprehensive comparison covering:
1. Budget comparison (which spent more, ROI analysis)
2. Revenue comparison (box office performance)
3. Runtime comparison (length differences)
4. Sentiment/tone comparison (based on overviews)
5. Genre differences
6. Overall assessment (which movie performed better overall and why)

Return JSON:
{{
  "comparison": {{
    "budget_analysis": "text",
    "revenue_analysis": "text",
    "runtime_analysis": "text",
    "sentiment_analysis": "text",
    "genre_analysis": "text",
    "overall_assessment": "text"
  }},
  "winner": {{
    "movieId": 123,
    "title": "Movie Title",
    "reasoning": "why this movie is better overall"
  }}
}}"""

