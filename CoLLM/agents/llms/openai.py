""" An LLM player is provided with a prompt describing the task and the current state of the environment.
"""

from openai import OpenAI
from CoLLM.agents.llms.base import LLMAgent
from pydantic import BaseModel
import openai


class Combination(BaseModel):
    reasoning: str
    first_item: str
    second_item: str


class OpenAIAgent(LLMAgent):
    def __init__(self, seed, multiagent, **kwargs):
        self.seed = seed
        super().__init__(seed=seed, multiagent=multiagent, **kwargs)
        self.setup(multiagent)
        self.client = OpenAI(api_key="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")  # your key here
        self.model = "gpt-4.1-2025-04-14"
        #self.model = "o4-mini"
        #self.temperature = 1.0
        self.max_tokens = 1000

    def prompt(self, input):
        # Create the user message from the input string
        user_message = {
            "role": "user",
            "content": input
        }
        
        # Create a system message to instruct the model to return structured JSON
        system_message = {
            "role": "system",
            "content": "You must respond with valid JSON in the following format: {\"reasoning\": \"your reasoning here\", \"first_item\": \"first item\", \"second_item\": \"second item\"}"
        }
        
        # Combine system and user messages
        messages = [system_message, user_message]
        
        response = openai.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"}
        )
        
        response_text = response.choices[0].message.content
        print(response_text)
        
        try:
            # Use Pydantic's built-in JSON parsing
            output = Combination.model_validate_json(response_text)
            
            # Return the structured output similar to Gemini agent
            return [output.first_item, output.second_item], response_text
            
        except Exception as e:
            print(f"Error parsing structured output: {e}, response was: {response_text}")
            # Fallback to the old parsing method
            return self.parse_input(response_text), response_text
