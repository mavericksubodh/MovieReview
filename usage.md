1. add .env file with parameter - OPENAI_API_KEY=
2. To Enrich Movie Data
   This command fetches movies from the database, enriches them with data from the LLM, and saves them to a new movies_enriched table.
         python main.py enrich --sample_size 100
              --sample_size is optional. It defaults to 50
         python main.py --all
              this will take all the movies for enrichment
         python main.py enrich --movie_id 11324
              enrich a specific movie, as search will work only on the 
      
2. Get Movie Recommendations
   Once the data is enriched, you can ask for recommendations based on a natural language query.
         python main.py recommend "a high-budget action movie with positive reviews"
      for system to return a movie it must be enriched. search will not result if there is not enriched data. 
3. Summarize User Preferences
   Generate a summary of a user's movie tastes based on their rating history.
          python main.py summarize
                Replace 1 with any userId from the ratings table.

4. Compare Movies
   Provide two or more movie IDs to get a detailed, side-by-side comparison from the LLM.
         python main.py compare 1 2
                Replace 1 and 2 with any movieIds from the movies table.
5. Verify results using queries :
   sqlite3 -header -column db/movies_attributes_v2.db "SELECT * FROM movies where movieid in (10885,11324,178314)  ORDER BY movieId;"
   sqlite3 -header -column db/movies_attributes_v2.db "SELECT * FROM movies_enriched where movieid in (10885,11324,178314)  ORDER BY movieId;"