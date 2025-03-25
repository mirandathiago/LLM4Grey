import json
import copy
from google import genai
from google.genai.types import GenerateContentConfig


from .model import Model
from config import RESPONSE_SCHEMA


class Gemini_2_0(Model):

    def __init__(self, api_key: str):
        super().__init__(api_key)    
        self.client = genai.Client(api_key=self.api_key)    
        

    def execute(self, system_prompt: str, user_prompt: str, temperature: float) -> dict:
        
       schema = copy.deepcopy(RESPONSE_SCHEMA["json_schema"]["schema"])
       schema.pop("additionalProperties", None) 
       
       response = self.client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_prompt,
        config=GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=400,
            temperature=temperature,
            response_mime_type='application/json',
            response_schema=schema
        ),
        )
       

       return response.text 
       
       
       