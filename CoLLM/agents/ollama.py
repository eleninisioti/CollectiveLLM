""" An LLM player is provided with a prompt describing the task and the current state of the environment.
"""

import ollama
from CoLLM.agents.base import Agent

class OllamaAgent(Agent):

    def __init__(self, seed, multiagent, forbid_repeats=False,**kwargs):
        self.forbid_repeats = forbid_repeats
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

    def _get_action(self):
        
        

        # Convert inventory (a list of strings) into a comma-separated string
        inventory_str = "\n Inventory: " + ", ".join(self.env.inventory)
        invalid_attempts_str = ", ".join([f"'{item1}' and '{item2}'" for item1, item2 in self.env.invalid_attempts])
        valid_attempts_str = ", ".join([f"'{item1}' and '{item2}' -> '{item3}'" for item1, item2, item3 in self.env.valid_attempts])
        current_obs = inventory_str + "\n Task valid combinations: " + valid_attempts_str + "\n Task invalid combinations: " + invalid_attempts_str
        state = self.intro + current_obs

        print(current_obs)

        response = ollama.chat(model='llama3.3', messages=[
            {
                'role': 'user',
                'content': state,
            },
        ])
        response = response['message']['content']
        action = self.parse_input(response)
        
        print(response)
        if not len(action[0]) and not len(action[1]):
            self.invalid_actions += 1

        return action, response
