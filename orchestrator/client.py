import os
from groq import Groq
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
client = groq
MODEL = "llama-3.1-8b-instant"

class LLMClient:
    def __init__(self):
        self.client = groq
        self.model = MODEL

    def get_response(self, prompt: str,tools:Optional[List[Dict[str, Any]]]=None):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            tools=tools,
            tool_choice="auto",
            max_tokens=4096
        )
        return response.choices[0].message.content
