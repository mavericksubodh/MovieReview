import sys
import os

# This allows the script to find and import modules from the project's root directory.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from llm_client import LLMClient
from prompts import Prompts

class SQLQueryGenerator:
    def __init__(self):
        self.llm_client = LLMClient()

    def generate_sql_query(self, user_input: str) -> str:
        system_message = Prompts.get_query_generation_system_message()
        user_prompt = Prompts.build_query_generation_prompt(user_input)

        # Use LLMClient for text generation with temperature=0.0 for deterministic SQL generation
        response = self.llm_client.generate_text(
            prompt=user_prompt,
            system_message=system_message,
            temperature=0.0
        )
        
        # Assuming the model returns only the SQL query string
        return response.strip()

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
    
    user_request_4 = "Summarize preferences for userID 2 based on their ratings and movie overviews"
    sql_query_4 = query_generator.generate_sql_query(user_request_4)
    print(f"User Request: {user_request_4}")
    print(f"Generated SQL Query:\n{sql_query_4}\n")
    
