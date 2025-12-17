import os
from dotenv import load_dotenv
import openai

from ..prompts import Prompts

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

class SQLQueryGenerator:
    def __init__(self):
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        self.client = openai.OpenAI()
        self.model_name = "gpt-3.5-turbo" # Or "gpt-4", "gpt-4o", etc.

    def generate_sql_query(self, user_input: str) -> str:
        system_message = Prompts.get_query_generation_system_message()
        user_prompt = Prompts.build_query_generation_prompt(user_input)

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.0, # Aim for deterministic SQL generation
            max_tokens=500 # Limit response length for SQL queries
        )
        
        # Assuming the model returns only the SQL query string
        return response.choices[0].message.content.strip()

if __name__ == '__main__':
    # Example usage
    query_generator = SQLQueryGenerator()

    user_request_1 = "Recommend action movies with high revenue and positive sentiment"
    sql_query_1 = query_generator.generate_sql_query(user_request_1)
    print(f"User Request: {user_request_1}")
    print(f"Generated SQL Query:\n{sql_query_1}\n")

    user_request_2 = "Show me 5 comedy movies released after 2010 with a high average rating"
    sql_query_2 = query_generator.generate_sql_query(user_request_2)
    print(f"User Request: {user_request_2}")
    print(f"Generated SQL Query:\n{sql_query_2}\n")

    user_request_3 = "List movies with a budget tier of 'high' and production effectiveness of 'high'"
    sql_query_3 = query_generator.generate_sql_query(user_request_3)
    print(f"User Request: {user_request_3}")
    print(f"Generated SQL Query:\n{sql_query_3}\n")
