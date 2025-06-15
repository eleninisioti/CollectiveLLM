""" An LLM player is provided with a prompt describing the task and the current state of the environment.
"""

import ollama
from CoLLM.agents.llms.base import LLMAgent
import re


class OllamaAgent(LLMAgent):

    def __init__(self, seed, multiagent, **kwargs):
        self.seed = seed
        
        super().__init__(**kwargs)
        self.setup( multiagent)


    def postprocess_action(self, actions):
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
        response = ollama.chat(model='llama3.3', messages=[
        {
            'role': 'user',
            'content': input,
        },])
        response = response['message']['content']
        return response
    
    def postprocess_relevance(self, text):
        try:
            # Find all numbers (including decimals) in the string
            numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
            if numbers:
                relevance_value = float(numbers[-1])
            else:
                raise ValueError("No number found in response")
        except Exception as e:
            print(f"Error extracting relevance: {e}, response was: {text}")
            relevance_value = 0.0
        return relevance_value
            
