import json
from openai import OpenAI
from config import RESPONSE_SCHEMA
from .model import Model
import re

class Deepseek_r1(Model):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = OpenAI(api_key=self.api_key,base_url="https://api.deepseek.com",)
        self.model_name = "deepseek-reasoner"
        self.schema = RESPONSE_SCHEMA  

    def execute(self, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> str:
        developer_prompt = {"role": "system", "content": system_prompt}
        user_prompt_formatted = {"role": "user", "content": user_prompt}

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[developer_prompt, user_prompt_formatted],
                temperature=temperature,
                max_tokens=400,
                
            )

           

            raw = response.choices[0].message.content.strip()
            if raw.startswith("```json"):
                raw = raw.removeprefix("```json").removesuffix("```").strip()
            elif raw.startswith("```"):
                raw = raw.removeprefix("```").removesuffix("```").strip()

            parsed = json.loads(raw)
            return json.dumps(parsed, ensure_ascii=False)

        except Exception as e:
            return json.dumps({"error": str(e)})
