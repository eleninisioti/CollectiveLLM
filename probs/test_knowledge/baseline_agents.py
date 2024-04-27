from probs.test_knowledge.base_agent import Agent
from collections import Counter
import numpy as np
import time
import random
import os


def softmax_with_temperature(logits, temperature):
    logits = np.array(logits)
    # Apply temperature scaling
    logits = logits/temperature

    # Compute softmax
    exp_logits = np.exp(logits)
    softmax_probs = exp_logits / np.sum(exp_logits)

    return softmax_probs

class RandomAgent(Agent):
    """" Chooses two random items from the inventory.
    """

    def __init__(self, forbid_repeats,  **kwargs):
        self.forbid_repeats = forbid_repeats
        super().__init__(**kwargs)

    def _get_action(self):
        inventory = self.env.wordcraft_env.env.env.table
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

    def query_knowledge(self, state="", current_step=9):

        random_word1 = random.sample(list(self.env.wordcraft_env.env.recipe_book.entities),1)[0]

        output = "Result: '" + random_word1 + "'"
        return output



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



class UncertaintyAgent(Agent):
    """ Chooses the two items from the inventory that have the highest uncertainty.

     Uncertainty is calculated as ...
     """

    def __init__(self, forbid_repeats, **kwargs):
        self.forbid_repeats = forbid_repeats
        super().__init__(**kwargs)

    def _get_action(self, current_step):
        past_actions = []
        for combin in self.past_actions:
            try:
                past_actions.append(combin[0])
                past_actions.append(combin[1])

            except:
                print("check")

        for el in self.env.wordcraft_env.env.env.table:
            index_el = self.env.word_to_index(el)
            if index_el not in self.past_actions:
                past_actions.append(index_el)
        words = list(Counter(past_actions).keys())
        freq = list(Counter(past_actions).values())

        uncertainty_values = []
        for el in freq:
            print(current_step)
            uncertainty_values.append(np.sqrt(np.log(current_step + 1) / (el + 1)))

        probs = softmax_with_temperature(uncertainty_values, temperature=0.1)
        if sum(uncertainty_values):
            choices = random.choices(words, weights=probs, k=2)
        else:
            choices = random.choices(words, k=2)
        first_word = choices[0]
        second_word = choices[1]

        first_word = self.env.index_to_word(first_word)
        second_word = self.env.index_to_word(second_word)
        return first_word, second_word


    def query(self, current_step=0, state=""):

        random_word1, random_word2 = self._get_action(current_step)
        counter =0
        if self.forbid_repeats:
            already_played = ([self.env.word_to_index(random_word1), self.env.word_to_index(random_word2)] in self.past_actions)
            while already_played and counter<20:
                random_word1, random_word2 = self._get_action(current_step)

                already_played = ([self.env.word_to_index(random_word1), self.env.word_to_index(random_word2)] in self.past_actions)
                counter += 1
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
            from wordcraft.recipe_book import Recipe
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

class EmpowerAgent(Agent):

    def __init__(self, forbid_repeats, **kwargs):
        self.forbid_repeats = forbid_repeats
        super().__init__(**kwargs)

    def query(self, current_step=0, state=""):
        recipes = self.env.wordcraft_env.recipe_book.entity2recipes
        all_combs = []
        for el1 in self.env.wordcraft_env.table:
            for el2 in self.env.wordcraft_env.table:
                if [el2, el1] not in all_combs and [el1, el2] not in all_combs:
                    all_combs.append([el1, el2])

        empower_values = []
        for comb in all_combs:
            os.chdir("wordcraft")
            from wordcraft.recipe_book import Recipe
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

        empower_values = softmax_with_temperature(empower_values, temperature=0.1)


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

class NoisyEmpowerAgent(Agent):

    def __init__(self, forbid_repeats, **kwargs):
        self.forbid_repeats = forbid_repeats
        super().__init__(**kwargs)

    def query(self, current_step=0, state=""):
        recipes = self.env.wordcraft_env.recipe_book.entity2recipes
        all_combs = []
        for el1 in self.env.wordcraft_env.table:
            for el2 in self.env.wordcraft_env.table:
                if [el2, el1] not in all_combs and [el1, el2] not in all_combs:
                    all_combs.append([el1, el2])

        empower_values = []
        for comb in all_combs:
            os.chdir("wordcraft")
            from wordcraft.recipe_book import Recipe
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
        empower_values = [value + np.random.normal(0, 50) for value in empower_values]
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

class Noisyv2EmpowerAgent(Agent):

    def __init__(self, forbid_repeats, **kwargs):
        self.forbid_repeats = forbid_repeats
        super().__init__(**kwargs)

    def query(self, current_step=0, state=""):
        recipes = self.env.wordcraft_env.recipe_book.entity2recipes
        all_combs = []
        for el1 in self.env.wordcraft_env.table:
            for el2 in self.env.wordcraft_env.table:
                if [el2, el1] not in all_combs and [el1, el2] not in all_combs:
                    all_combs.append([el1, el2])

        empower_values = []
        for comb in all_combs:
            os.chdir("wordcraft")
            from wordcraft.recipe_book import Recipe
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

        small_number = np.random.rand()
        if small_number < 0.9:
            empower_values = [1]*len(empower_values)
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

class EmpowerOnestepAgent(Agent):

    def __init__(self, forbid_repeats, **kwargs):
        self.forbid_repeats = forbid_repeats
        super().__init__(**kwargs)

    def query(self, current_step=0, state=""):
        recipes = self.env.wordcraft_env.recipe_book.entity2recipes
        all_combs = []

        # add elements of others to table
        for neigh in self.neighbors:
            new_table = self.env.wordcraft_env.table
            for el in new_table:
                if el not in self.env.wordcraft_env.table:
                    self.env.wordcraft_env.table.append(el)

        for el1 in self.env.wordcraft_env.table:
            for el2 in self.env.wordcraft_env.table:
                if [el2, el1] not in all_combs and [el1, el2] not in all_combs:
                    all_combs.append([el1, el2])

        empower_values = []
        for comb in all_combs:
            os.chdir("wordcraft")
            from wordcraft.recipe_book import Recipe
            os.chdir("..")
            recipe = Recipe(comb)
            new_el = self.env.wordcraft_env.recipe_book.evaluate_recipe(recipe)
            empower_value = 0
            for el, pot_recipes in recipes.items():
                for pot_recipe in pot_recipes:
                    parts = list(pot_recipe.keys())
                    if new_el in parts:
                        other_exists = sum([1 if el in parts else 0 for el in self.env.wordcraft_env.table])
                        if other_exists:
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
            while action in self.past_actions and counter < 60:
                chosen_index += 1
                first_word = sorted_combs[chosen_index][0]
                second_word = sorted_combs[chosen_index][1]
                action = [int(self.env.wordcraft_env.table.index(first_word)), int(self.env.wordcraft_env.table.index(second_word))]
                counter +=1

        output = "Combination: '" + first_word + "' and '" + second_word + "'"
        return output

