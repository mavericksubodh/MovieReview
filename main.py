import sqlite3
import os
import sys
from dotenv import load_dotenv
# from GenericAgent import GenericAgent
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

load_dotenv()

# question = sys.argv[1] if len(sys.argv) > 1 else None
# if not question:
#     print('Usage: python main.py "YOUR_QUESTION"')
#     sys.exit(1)

# agent = GenericAgent(
#     # provider=os.getenv("provider", "openai"),
#     provider=os.getenv("provider", "gemini"),
#     project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
#     openai_api_key=os.getenv("OPENAI_API_KEY"),
# )

# agent.generate_content(question)


#
# agent = GenericAgent(provider="gemini")
# agent.generate_content("Hello from Gemini!")
#
# agent = GenericAgent(provider="openai")
# agent.generate_content("Hello from Gemini!")


# movie_db= ['db/movies_attributes_v2.db','db/ratings.db']
# movie_db= ['db/ratings.db']
movie_db= ['db/movies_attributes_v2.db']

# model = SentenceTransformer('all-MiniLM-L6-v2')
# index = faiss.IndexFlatL2(model.get_sentence_embedding_dimension())


def get_db_data(db):
    try:
        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables=cursor.fetchall()
            print(f"Tables in {db}: {tables}")

            for table in tables :
                table_name = table[0]
                cursor.execute(f"SELECT * FROM {table_name};")
                # cursor.execute(f"SELECT userId, count(*) as rating_count  FROM {table_name} group by userId ORDER BY rating_count DESC;")
                records=cursor.fetchall()
                print(f"records: {records}")

    except sqlite3.Error as error:
        print(f"Error while connecting to {db}: {error}")


for db in movie_db :
    get_db_data(db)