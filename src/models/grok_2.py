import json
from openai import OpenAI
from config import RESPONSE_SCHEMA
from .model import Model

class Grok_2(Model):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = OpenAI(api_key=self.api_key,base_url="https://api.x.ai/v1",)
        self.model_name = "grok-2-latest"
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
                response_format=self.schema
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return json.dumps({"error": str(e)})
