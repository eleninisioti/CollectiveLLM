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


    def parse_input(self, actions):
        def find_nth(haystack, needle, n):
            """ Find the nth occurrence of sub-string in string.
            """
            temp = haystack.find("Combination")
            start = haystack.find(needle)
            while start >= 0 and n > 1:
                start = haystack.find(needle, start + len(needle))
                n -= 1
            return start
    
        start_first = find_nth(actions, "Combination: '", 1)
        actions = actions[start_first:]
        start_first = find_nth(actions, "Combination: '", 1)
        end_first = find_nth(actions, "'", 2)
        first_word = actions[start_first + len("Combination: '"):end_first]
        end_second = find_nth(actions, "'", 4)
        second_word = actions[(end_first + 7): end_second]
        return first_word, second_word

    def prompt(self, input):
        client = genai.Client(api_key="AIzaSyAyein0EWwqLj9irFnwo2aYX-kqOSQZsu4")

        response = client.models.generate_content(
            model="gemini-2.0-flash",
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
    
            
