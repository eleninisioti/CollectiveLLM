from CoLLM.agents.base import Agent
from CoLLM.utils import softmax_with_temperature
import numpy as np
import pickle



class EmpowerAgent(Agent):

    def __init__(self, **kwargs):
        self.forbid_repeats = True # this agent is deterministic so it won't work if we don't forbid repeats
        super().__init__(**kwargs)
        
        with open('data_empower_values.pkl', 'rb') as f:
            self.empower_values = pickle.load(f)

    def _get_action(self, current_memory):
        recipes = self.env.recipe_book["entities"]
        indiv_inventory = self.env.inventory
        
                
        social_inventory = self.get_social_inventory()
        social_inventory =[el for el in social_inventory if el not in indiv_inventory]
        inventory = list(set(indiv_inventory) | set(social_inventory))
        
        
        
        print("Agent ", self.idx)
        print("invenotry", inventory)
        print(len(indiv_inventory), len(inventory), len(social_inventory))
        print("social", social_inventory)
        all_combs = []
        for el1 in inventory:
            for el2 in inventory:
                if [el2, el1] not in all_combs and [el1, el2] not in all_combs:
                    if (el1, el2) not in self.env.valid_attempts:
                        all_combs.append([el1, el2])

        empower_values = []
        for comb in all_combs:
            if tuple(comb) in self.empower_values:
                empower_values.append(self.empower_values[tuple(comb)])
            else:
                empower_values.append(0)

        # Sample with probability proportional to empower_values
        # Convert to probabilities using softmax
        empower_values = softmax_with_temperature(empower_values, temperature=40)

        chosen_index = 0
        sorted_combs = [x for _, x in sorted(zip(empower_values, all_combs))]
        sorted_combs.reverse()

        first_word = sorted_combs[chosen_index][0]
        second_word = sorted_combs[chosen_index][1]

        action = [first_word, second_word]
        print(action, self.empower_values[tuple(action)] if tuple(action) in self.empower_values.keys() else 0)

        return action, "", indiv_inventory
