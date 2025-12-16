import sqlite3

# movie_db= ['db/movies_attributes_v2.db','db/ratings.db']
# movie_db= ['db/ratings.db']
movie_db= ['db/movies_attributes_v2.db']

for db in movie_db :
    try:
        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables=cursor.fetchall()
            print(f"Tables in {db}: {tables}")

            for table in tables :
                table_name = table[0]
                cursor.execute(f"SELECT * FROM {table_name}")
                # cursor.execute(f"SELECT userId, count(*) as rating_count  FROM {table_name} group by userId ORDER BY rating_count DESC;")
                # cursor.execute(f"select * from {table_name} where title like '%Shutter%' ")
                # cursor.execute(f"-- select * from {table_name} where  movieID=11324")
                cursor.execute(f"SELECT movieId FROM {table_name}")
                records=cursor.fetchall()
                print(f"records: {records}")


    except sqlite3.Error as error:
        print(f"Error while connecting to {db}: {error}")

