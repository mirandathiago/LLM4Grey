import json
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from config import RESPONSE_SCHEMA
from .model import Model

class Claude_3_5(Model):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = Anthropic(api_key=self.api_key)
        self.model_name = "claude-3-5-sonnet-20241022"

        self.schema = RESPONSE_SCHEMA["json_schema"]["schema"]

    def execute(self, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> dict:
        try:
            response = self.client.messages.create(
                model=self.model_name,
                system=system_prompt,
                max_tokens=400,
                temperature=temperature,
                tools=[
                {
                    "name": "discussion_analysis_schema",
                    "description": "Classify the discussion for inclusion in the review.",
                    "input_schema": self.schema  
                }
            ],
            tool_choice={"type": "tool", "name": "discussion_analysis_schema"},
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                
            )

            
            
            for content in response.content:
            
                if content.type == 'tool_use':
                    
                    tool_name = content.name
                    tool_input = content.input
                    
                    
                    #print(f"Tool Name: {tool_name}")
                    #print("Tool Input:")
                    return json.dumps(tool_input)
                
               
                elif content.type == 'text':
                    #print("Additional Text Response:")
                    #print(content.text)
                    pass


        except Exception as e:
            return {"error": str(e)}
