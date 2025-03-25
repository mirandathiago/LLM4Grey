from abc import ABC, abstractmethod
import json

class Model(ABC):
   

    def __init__(self, api_key: str):
        
        self.api_key = api_key
       

    @abstractmethod
    def execute(self, system_prompt: str, user_prompt: str, temperature: float) -> dict:
        pass
