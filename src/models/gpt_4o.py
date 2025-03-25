import json
import os
from openai import OpenAI

from config import RESPONSE_SCHEMA


from .model import Model



class Gpt_4o(Model):

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = OpenAI(api_key=self.api_key) 
    

   

    def execute(self, system_prompt: str, user_prompt: str, temperature: float) -> dict:
        developer_prompt = {
            "role": "system",
            "content": system_prompt
        }

        user_prompt_formatted = {
            "role": "user",
            "content": user_prompt
        }

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[developer_prompt, user_prompt_formatted],
            max_tokens=400,
            temperature=temperature,
            response_format=RESPONSE_SCHEMA
        )

        return response.choices[0].message.content.strip()
        