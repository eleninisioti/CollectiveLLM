""" An LLM player is provided with a prompt describing the task and the current state of the environment.
"""

import ollama
from CoLLM.agents.base import Agent
import random

class LLMAgent(Agent):

    def __init__(self, seed, multiagent, **kwargs):
        self.seed = seed

       
        super().__init__(**kwargs)

        self.setup( multiagent)
        

    def setup(self, multiagent):
        if  multiagent:
            prompt_file = "la2/prompts/multitxt"
        else:
            prompt_file = "la2/prompts/single.txt"

        temp = open(prompt_file, 'r').readlines()
        self.intro = " ".join(temp)
        
    
    

    

    def _get_action(self,  current_memory):
        
        

        # Convert inventory (a list of strings) into a comma-separated string
        inventory_str = "\n Inventory: " + ", ".join(self.env.inventory)   
        
        current_memory = self.fetch_memory(inventory_str)
        state = self.intro + inventory_str + current_memory
        
        action, response = self.prompt(state)
        
        #action = self.postprocess_action(response)
        
        print(response)
        if not len(action[0]) and not len(action[1]):
            self.invalid_actions += 1

        return action, response
