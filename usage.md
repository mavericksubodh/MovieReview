1. add .env file with parameter - OPENAI_API_KEY=
2. To Enrich Movie Data
   This command fetches movies from the database, enriches them with data from the LLM, and saves them to a new movies_enriched table.
         python main.py enrich --size 100
              --size is optional. It defaults to 50
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
          python main.py summarize 2
                Replace 1 with any userId from the ratings table.

4. Compare Movies
   Provide two or more movie IDs to get a detailed, side-by-side comparison from the LLM.
         python main.py compare 1 2
                Replace 1 and 2 with any movieIds from the movies table.
5. Helping results for test verifications :

   sqlite3 -header -column db/movies_attributes_v2.db "SELECT * FROM movies where movieid in (10885,11324,178314)  ORDER BY movieId;"
   sqlite3 -header -column db/movies_attributes_v2.db "SELECT * FROM movies_enriched where movieid in (10885,11324,178314)  ORDER BY movieId;"
   sqlite3 -header -column db/movies_attributes_v2.db "SELECT m.* FROM movies as m, movies_enriched me  where m.movieid = me.movieid;"
   sqlite3 -header -column db/ratings.db "SELECT count(distinct ( movieid) ) from ratings;"  
   sqlite3 -header -column db/movies_attributes_v2.db "SELECT count(distinct ( movieid) ) from movies_enriched;" 
6. Alternate path :
   Generate queries using LLM and send data to LLM for verification and similarity checks. 
   
   sqlite3 -header -column db/movies_attributes_v2.db " ATTACH DATABASE 'db/ratings.db' AS ratings_db; SELECT m.title, m.overview, m.genres, me.sentiment, me.revenue_tier, me.budget_tier, me.production_effectiveness, me.age_category, AVG(r.rating) AS average_rating FROM movies AS m JOIN movies_enriched AS me ON m.movieId = me.movieId LEFT JOIN ratings AS r ON m.movieId = r.movieId GROUP BY m.movieId ORDER BY average_rating DESC, m.revenue DESC LIMIT 10;"


   sqlite3 -header -column db/movies_attributes_v2.db " ATTACH DATABASE 'db/ratings.db' AS ratings_db; SELECT r.userId, m.title, m.overview, m.genres, me.sentiment, me.revenue_tier, me.budget_tier, me.production_effectiveness, me.age_category, AVG(r.rating) AS average_rating FROM movies AS m JOIN movies_enriched AS me ON m.movieId = me.movieId JOIN ratings_db.ratings AS r ON m.movieId = r.movieId WHERE r.userId = 1 GROUP BY m.movieId, r.userId ORDER BY average_rating DESC;"

   sqlite3 -header -column db/movies_attributes_v2.db " ATTACH DATABASE 'db/ratings.db' AS ratings_db; SELECT COUNT(DISTINCT r.movieId) as movies_with_ratings,COUNT(DISTINCT me.movieId) as movies_with_enrichment, COUNT(DISTINCT CASE WHEN me.movieId IS NOT NULL THEN r.movieId END) as movies_with_both FROM ratings_db.ratings AS r LEFT JOIN movies_enriched AS me ON r.movieId = me.movieId WHERE r.userId = 1;" 
   sqlite3 -header -column db/movies_attributes_v2.db " ATTACH DATABASE 'db/ratings.db' AS ratings_db; SELECT r.userId, m.title, m.overview, m.genres, me.sentiment, me.revenue_tier, me.budget_tier, me.production_effectiveness, me.age_category, AVG(r.rating) AS average_rating FROM movies AS m JOIN movies_enriched AS me ON m.movieId = me.movieId JOIN ratings_db.ratings AS r ON m.movieId = r.movieId WHERE r.userId = 1 GROUP BY m.movieId, r.userId ORDER BY average_rating DESC;"
