from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional

from recommender import MovieRecommender

# --- 1. Initialize the FastAPI app ---
app = FastAPI(
    title="Movie Recommender API",
    description="An API that recommends movies based on semantic search and metadata filtering.",
    version="1.0.0"
)

# --- 2. Load the recommender model (Singleton Pattern) ---
recommender = MovieRecommender()

# --- 3. Define Request and Response Models using Pydantic ---
class RecommendationRequest(BaseModel):
    """The request body for the /recommend endpoint."""
    query: str = Field(..., description="The user's search query (e.g., 'a movie about space').")
    top_k: int = Field(5, gt=0, le=20, description="The number of recommendations to return.")
    min_runtime: Optional[int] = Field(None, gt=0, description="The minimum runtime in minutes.")
    max_runtime: Optional[int] = Field(None, gt=0, description="The maximum runtime in minutes.")
    genres: Optional[List[str]] = Field(None, description="A list of genres to include.")
    release_era: Optional[str] = Field(None, description="The release era (e.g., 'Modern', '2010s').")
    min_budget: Optional[int] = Field(None, gt=0, description="The minimum budget of the movie.")
    min_revenue: Optional[int] = Field(None, gt=0, description="The minimum revenue of the movie.")
    audience: Optional[str] = Field(None, description="The audience rating (e.g., 'PG13', 'Adult Only').")

class MovieResponse(BaseModel):
    """The response model for a single movie recommendation."""
    movieId: int
    title: str
    overview: Optional[str]
    genres: Optional[str]
    releaseEra: Optional[str]
    runtime: Optional[int]
    revenue: Optional[int]
    budget: Optional[int]
    Audience: Optional[str]

# --- 4. Create the API Endpoint ---
@app.post("/recommend/", response_model=List[MovieResponse])
def get_recommendations(request: RecommendationRequest):
    """
    Takes a user query and filters, and returns a list of recommended movies.
    """
    recommendations = recommender.recommend(
        query=request.query,
        top_k=request.top_k,
        min_runtime=request.min_runtime,
        max_runtime=request.max_runtime,
        genres=request.genres,
        release_era=request.release_era,
        min_budget=request.min_budget,
        min_revenue=request.min_revenue,
        audience=request.audience
    )
    return recommendations

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Movie Recommender API is running. Go to /docs for documentation."}

# To run this application:
# 1. Install FastAPI and Uvicorn: pip install fastapi "uvicorn[standard]"
# 2. Run the server: uvicorn main:app --reload
