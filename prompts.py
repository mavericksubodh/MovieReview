import json
from typing import List, Dict

class Prompts:
    # --- Single Enrichment (Original) ---
    @staticmethod
    def get_enrichment_system_message() -> str:
        return "You are a movie data analyst. Always return valid JSON only."

    @staticmethod
    def build_enrichment_prompt(movie: Dict, avg_rating: float) -> str:
        # This prompt is kept for reference or single-use cases
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

    # --- Batch Enrichment (New) ---
    @staticmethod
    def get_batch_enrichment_system_message() -> str:
        return """You are a highly efficient movie data analyst. You will be given a JSON array of movie objects.
For each movie object in the input array, you must generate a corresponding JSON object with the 5 requested attributes.
Return a single JSON object with one key, "enriched_movies", which contains a JSON array of the results.
The order of the movies in the output array MUST EXACTLY match the order of the movies in the input array."""

    @staticmethod
    def build_batch_enrichment_prompt(movies: List[Dict]) -> str:
        movies_json_string = json.dumps(movies, indent=2)
        return f"""Analyze the following list of movies and generate 5 attributes for each.

Input Movies:
{movies_json_string}

For each movie, generate these attributes:
1. sentiment: positive/neutral/negative (based on overview tone)
2. budget_tier: low/medium/high (reason about industry standards)
3. revenue_tier: low/medium/high (reason about box office performance)
4. production_effectiveness: low/medium/high (analyze rating, budget-to-revenue ratio, and overall success)
5. age_category: kid/teen/adult (based on content and themes)

Return ONLY a single valid JSON object in the following format, with one entry for each movie from the input list, in the same order:
{{
  "enriched_movies": [
    {{
      "sentiment": "...",
      "budget_tier": "...",
      "revenue_tier": "...",
      "production_effectiveness": "...",
      "age_category": "..."
    }},
    {{
      "sentiment": "...",
      "budget_tier": "...",
      "revenue_tier": "...",
      "production_effectiveness": "...",
      "age_category": "..."
    }}
  ]
}}"""

    # --- Other Prompts ---
    @staticmethod
    def get_recommendation_system_message() -> str:
        return "You are a movie recommendation expert. Return valid JSON with movie recommendations."
    
    @staticmethod
    def build_recommendation_prompt(query: str, movies_data: List[Dict]) -> str:
        movies_json = json.dumps(movies_data, indent=2)
        return f"""Given the following ENRICHED MOVIE DATASET, generate personalized recommendations.

User Query: {query}

Movie Dataset:
{movies_json}

IMPORTANT RULES FOR RECOMMENDATIONS:
1.  **ONLY recommend movies that are present in the provided "Movie Dataset" above.** Do NOT invent new movies or movie IDs.
2.  For each recommendation, the `movieId` MUST be one of the `movieId`s from the "Movie Dataset".
3.  Analyze the dataset and recommend 5 movies that best match the user's criteria. If fewer than 5 suitable movies are found within the provided dataset, recommend only those found.

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

    @staticmethod
    def get_query_generation_system_message() -> str:
        return "You are an expert SQL query generator. Your task is to convert natural language requests into SQL queries for a movie database. Always return only the SQL query, and nothing else."

    @staticmethod
    def build_query_generation_prompt(user_query: str) -> str:
        return f"""Generate a SQLite SQL query based on the user's request.
The database has three tables: `movies`, `ratings`, and `movies_enriched`.

Table `movies`:
- `movieId` (INTEGER, PRIMARY KEY)
- `title` (TEXT)
- `overview` (TEXT)
- `budget` (INTEGER)
- `revenue` (INTEGER)
- `genres` (TEXT, JSON array of strings, e.g., '["Action", "Adventure"]')

Table `ratings`:
- `userId` (INTEGER)
- `movieId` (INTEGER, FOREIGN KEY to movies.movieId)
- `rating` (REAL)
- `timestamp` (INTEGER)

Table `movies_enriched`:
- `movieId` (INTEGER, PRIMARY KEY, FOREIGN KEY to movies.movieId)
- `sentiment` (TEXT, 'positive', 'neutral', or 'negative')
- `budget_tier` (TEXT, 'low', 'medium', or 'high')
- `revenue_tier` (TEXT, 'low', 'medium', or 'high')
- `production_effectiveness` (TEXT, 'low', 'medium', or 'high')
- `age_category` (TEXT, 'kid', 'teen', or 'adult')

Relationships:
- `movies.movieId` is linked to `ratings.movieId`
- `movies.movieId` is linked to `movies_enriched.movieId`

Your query should select `movies.title`, `movies.overview`, `movies.genres`, `movies_enriched.sentiment`, `movies_enriched.revenue_tier`, `movies_enriched.budget_tier`, `movies_enriched.production_effectiveness`, `movies_enriched.age_category`, and `AVG(ratings.rating)` (aliased as `average_rating`).
Ensure the query returns a maximum of 10 recommended movies.
Order the results by `average_rating` in descending order, and then by `movies.revenue` in descending order.
Handle genre filtering by checking if the genre string is present in the `genres` JSON array.

User Request: "{user_query}"

SQL Query:"""