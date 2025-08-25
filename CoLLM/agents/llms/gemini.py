""" An LLM player is provided with a prompt describing the task and the current state of the environment.
"""

from google import genai
from CoLLM.agents.llms.base import LLMAgent
from pydantic import BaseModel


class Combination(BaseModel):
    reasoning: str
    first_item: str
    second_item: str

class GeminiAgent(LLMAgent):

    def __init__(self, seed, multiagent,  **kwargs):
        self.seed = seed
        
        super().__init__(seed=seed, multiagent=multiagent, **kwargs)
        self.setup( multiagent)




    def prompt(self, input):
        client = genai.Client(api_key="AIzaSyAmSED4aucmokspKjfVseUjKWz2SSrqDGY")

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[input],
                config={
        "response_mime_type": "application/json",
        "response_schema": Combination,
    },
        )
        print(response.text)
        print(response.parsed)
        output = response.parsed
        return [output.first_item, output.second_item], response.text
        #return response.text
    
            
