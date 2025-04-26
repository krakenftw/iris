import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = "gpt-4o"

class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = MODEL

    def get_response(self, prompt: str, tools: Optional[List[Dict[str, Any]]] = None, max_tokens: int = 4096):
        messages = [{"role": "user", "content": prompt}]
        
        if tools:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=max_tokens
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens
            )
        
        return response
