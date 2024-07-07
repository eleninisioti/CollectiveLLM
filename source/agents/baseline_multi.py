""" Defines agents that are not LLMs (random, uncertainty, empower).
"""

from source.agents.base_agent import Agent
from collections import Counter
import numpy as np
import time
import random
import os


class CulturalEvolutionAgent(Agent):
    """" Chooses two random items from the inventory.
    """

    def __init__(self, forbid_repeats,  **kwargs):
        self.forbid_repeats = forbid_repeats
        super().__init__(**kwargs)

    def _get_action(self):
        inventory = self.env.wordcraft_env.env.env.table

        # add inventory of others
        for agent in self.neighbors:
            inventory.extend(agent.env.wordcraft_env.env.table)
        inventory = list(set(inventory))
        self.env.wordcraft_env.env.env.table = inventory
        random_loc = np.random.randint(0, len(inventory))
        random_word1 = inventory[random_loc]
        random_loc = np.random.randint(0, len(inventory))
        random_word2 = inventory[random_loc]

        return random_word1, random_word2

    def query(self, state="", current_step=9):

        random_word1, random_word2 = self._get_action()
        counter =0
        if self.forbid_repeats:
            already_played = ([self.env.word_to_index(random_word1), self.env.word_to_index(random_word2)] in self.past_actions)

            while already_played and counter < 20:
                print(self.past_actions)
                print([self.env.word_to_index(random_word1), self.env.word_to_index(random_word2)])
                random_word1, random_word2 = self._get_action()

                already_played = ([self.env.word_to_index(random_word1), self.env.word_to_index(random_word2)] in self.past_actions)
                counter+=1
        output = "Combination: '" + random_word1 + "' and '" + random_word2 + "'"
        return output

class EmpowerCulturalEvolutionAgent(Agent):

    def __init__(self, forbid_repeats, **kwargs):
        self.forbid_repeats = forbid_repeats
        super().__init__(**kwargs)

    def query(self, current_step=0, state=""):
        inventory = self.env.wordcraft_env.env.env.table

        # add inventory of others
        for agent in self.neighbors:
            inventory.extend(agent.env.wordcraft_env.env.table)
        inventory = list(set(inventory))
        self.env.wordcraft_env.env.env.table = inventory

        recipes = self.env.wordcraft_env.recipe_book.entity2recipes
        all_combs = []
        for el1 in self.env.wordcraft_env.table:
            for el2 in self.env.wordcraft_env.table:
                if [el2, el1] not in all_combs and [el1, el2] not in all_combs:
                    all_combs.append([el1, el2])

        empower_values = []
        for comb in all_combs:
            os.chdir("wordcraft")
            from wordcraft_todelete.recipe_book import Recipe
            os.chdir("..")

            recipe = Recipe(comb)
            new_el = self.env.wordcraft_env.recipe_book.evaluate_recipe(recipe)
            empower_value = 0
            for el, pot_recipes in recipes.items():
                for pot_recipe in pot_recipes:
                    parts = list(pot_recipe.keys())
                    if new_el in parts:
                        empower_value += 1
                        break
            empower_values.append(empower_value)

        chosen_index = 0

        sorted_combs = [x for _, x in sorted(zip(empower_values, all_combs))]
        sorted_combs.reverse()
        first_word = sorted_combs[chosen_index][0]
        second_word = sorted_combs[chosen_index][1]

        action = [int(self.env.wordcraft_env.table.index(first_word)), int(self.env.wordcraft_env.table.index(second_word))]
        counter = 0
        if self.forbid_repeats:

            while (action in self.past_actions) and (counter <60):
                chosen_index += 1
                first_word = sorted_combs[chosen_index][0]
                second_word = sorted_combs[chosen_index][1]
                action = [int(self.env.wordcraft_env.table.index(first_word)), int(self.env.wordcraft_env.table.index(second_word))]
                counter +=1

        print("counter is", counter, len(sorted_combs))
        output = "Combination: '" + first_word + "' and '" + second_word + "'"
        return output

