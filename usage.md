1. add .env file with parameter - OPENAI_API_KEY=
2. Enrich Movie Data
   This command fetches movies from the database, enriches them with data from the LLM, and saves them to a new movies_enriched table.
   Shell Script
   python main.py enrich --sample_size 100
   --sample_size is optional. It defaults to 50
   python main.py --all
     this will take all the movies for refinement  
2. Get Movie Recommendations
   Once the data is enriched, you can ask for recommendations based on a natural language query.
   Shell Script
   python main.py recommend "a high-budget action movie with positive reviews"
3. Summarize User Preferences
   Generate a summary of a user's movie tastes based on their rating history.
   Shell Script
   python main.py summarize 1

   Replace 1 with any userId from the ratings table.
4. Compare Movies
   Provide two or more movie IDs to get a detailed, side-by-side comparison from the LLM.
   Shell Script
   python main.py compare 1 2

   Replace 1 and 2 with any movieIds from the movies table.
