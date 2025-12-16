import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(
        self,
        openai_model: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ):
        from openai import OpenAI
        openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment or provided")
        self.client = OpenAI(api_key=openai_api_key)
        self.model = openai_model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    def generate(self, prompt: str, system_message: Optional[str] = None, json_mode: bool = True, temperature: float = 0.3) -> str:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"} if json_mode else None
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise
    
    def generate_text(self, prompt: str, system_message: Optional[str] = None, temperature: float = 0.7) -> str:
        return self.generate(prompt, system_message, json_mode=False, temperature=temperature)
