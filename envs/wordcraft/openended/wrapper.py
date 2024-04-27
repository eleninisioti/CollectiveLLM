import os
from enum import IntEnum

import numpy as np
import gym
from gym.utils import seeding
from wordcraft_openended.recipe_book import Recipe, RecipeBook


NO_RECIPE_PENALTY = -0.1
IRRELEVANT_RECIPE_PENALTY = -0.1
GOAL_REWARD = 1.0
SUBGOAL_REWARD = 1.0

import random
import string

class WordcraftEnvForLLM(gym.Env):

    def __init__(self, wordcraft_env, encoded):
        self.wordcraft_env = wordcraft_env
        self.wordcraft_env.success = False
        self.encoded = encoded

    def reset(self):
        self.past_invalid_combs = []
        self.past_valid_combs = {}
        return self.wordcraft_env.reset()


    def step(self, actions):
        # ---- first mixing step ----
        reward = 0
        if self.wordcraft_env.done:  # no-op if env is done

            return self._get_observation(), reward, self.wordcraft_env.done, {}

        # Handle invalid actions
        for action in actions:
            invalid_action = not (0 <= action < self.wordcraft_env.max_table_size)

        if invalid_action:
            print("invalid action inside env")
            self.wordcraft_env.episode_step += 1
            if self.wordcraft_env.episode_step >= self.wordcraft_env.max_steps:
                self.wordcraft_env.done = True

        # first word
        action = actions[0]
        i = self.wordcraft_env.table_index[action]
        e = self.wordcraft_env.recipe_book.entities[i]
        if self.encoded:
            new_comb = "'" + self.encode(e) + "'"

        else:
            new_comb = "'" + e + "'"


        selection_size = len(self.wordcraft_env.selection)
        self.wordcraft_env.selection.append(e)
        self.wordcraft_env.selection_index[selection_size] = i
        self.wordcraft_env.selection_features[selection_size, :] = self.wordcraft_env.feature_map.feature(e)
        selection_size = len(self.wordcraft_env.selection)

        # second word
        action = actions[1]
        self.wordcraft_env.episode_mix_steps += 1
        i = self.wordcraft_env.table_index[action]
        e = self.wordcraft_env.recipe_book.entities[i]
        if self.encoded:
            new_comb += " and '" + self.encode(e) + "'"

        else:
            new_comb += " and '" + e + "'"


        selection_size = len(self.wordcraft_env.selection)
        self.wordcraft_env.selection.append(e)
        self.wordcraft_env.selection_index[selection_size] = i
        self.wordcraft_env.selection_features[selection_size, :] = self.wordcraft_env.feature_map.feature(e)

        # Evaluate selection
        selection = self.wordcraft_env.selection
        recipe = Recipe(self.wordcraft_env.selection)
        result = self.wordcraft_env.recipe_book.evaluate_recipe(recipe)

        print("inside env:", new_comb, result)

        if result is None:
            reward = 0

        else:

            if result not in self.wordcraft_env.table:
                self.wordcraft_env.subgoal_history[new_comb] = result
                reward = 1

                result_i = self.wordcraft_env.recipe_book.entity2index[result]
                table_size = len(self.wordcraft_env.table)
                self.wordcraft_env.table.append(result)
                self.wordcraft_env.table_index[table_size] = result_i
                self.wordcraft_env.table_features[table_size, :] = self.wordcraft_env.feature_map.feature(result)

        self.wordcraft_env.episode_reward += reward

        # Clear selection
        self.wordcraft_env.reset_selection()

        self.wordcraft_env.episode_step += 1
        if self.wordcraft_env.episode_mix_steps >= self.wordcraft_env.max_mix_steps or self.wordcraft_env.episode_step >= self.wordcraft_env.max_steps:
            self.wordcraft_env.done = True

        obs = self.wordcraft_env.get_observation()
        self.wordcraft_env.remaining_rounds = self.wordcraft_env.max_mix_steps - self.wordcraft_env.episode_step

        info = {"remaining_rounds": self.wordcraft_env.remaining_rounds}

        if not reward:
            if actions not in self.past_invalid_combs:
                self.past_invalid_combs.append(tuple(actions))
        if result:
            if tuple(actions) not in self.past_valid_combs.keys():
                self.past_valid_combs[tuple(actions)] = self.wordcraft_env.env.env.table.index(result)
        return obs, reward, self.wordcraft_env.done, info


    def encode(self, word):
        length = 5
        random.seed(word)
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def index_to_word(self, index):
        print(index)
        return self.wordcraft_env.env.env.table[index]

    def word_to_index(self, word):
        items = list(self.wordcraft_env.env.recipe_book.entities)
        if self.encoded:
            items = [self.encode[el] for el in items]
        return items.index(word)

    def _display_llm(self):
        inventory = self.wordcraft_env.table
        if self.encoded:
            inventory = [self.encode(el) for el in inventory]
        remaining_rounds = self.wordcraft_env.max_mix_steps - self.wordcraft_env.episode_step
        valid_combs = ""
        counter = 0
        for key, val in self.past_valid_combs.items():
            subkeys = []
            for subkey in key:

                subkeys.append(str(self.index_to_word(subkey)))
            new_key = '"' + subkeys[0] + '" and "' + subkeys[1]
            val = str(self.index_to_word(val))
            if self.encoded:
                valid_combs += new_key + " -> " + self.encode(val) + " , "
            else:
                valid_combs += new_key + " -> " + val + " , "

            counter = counter + 1
            if counter > 15:
                break

        if self.encoded:
            past_invalid_combs = [self.encode(el) for el in self.past_invalid_combs]

        else:
            past_invalid_combs = self.past_invalid_combs

        past_invalid_combs = past_invalid_combs[-15:]
        past_invalid_combs_str = []
        for element in past_invalid_combs:

            past_invalid_combs_str.append('"' + str(self.index_to_word(element[0])) + '" and "' + str(self.index_to_word(element[1])) + '"')

        if self.encoded:
            self.wordcraft_env.env.env.table = [self.encode(el) for el in self.wordcraft_env.env.env.table]

        output = "\n<human> INPUT \n Inventory: '" + "', '".join(inventory) + "'"
        output += "\nTask valid combinations (do not repeat combinations here): " + valid_combs
        output += "\nTask invalid combinations (do not repeat combinations here): " + ", ".join(past_invalid_combs_str)
        return output

    def render(self, mode='human'):
        return self._display_llm()

    def invalid_combs_to_string(self, past_invalid_combs):
        past_invalid_combs_str = ""
        for element in past_invalid_combs:
            past_invalid_combs_str += '"' + str(self.index_to_word(element[0])) + '" and "' + str(
                self.index_to_word(element[1])) + '", '
        return past_invalid_combs_str, len(past_invalid_combs)

    def get_invalid_combs(self):
        "Returns invalid combinations as a string"
        if self.encoded:
            past_invalid_combs = [self.encode(el) for el in self.past_invalid_combs]

        else:
            past_invalid_combs = self.past_invalid_combs

        return past_invalid_combs[-15:], len(past_invalid_combs[-15:])

    def valid_combs_to_string(self, past_valid_combs):
        valid_combs = ""

        for key, val in self.past_valid_combs.items():

            subkeys = []
            for subkey in key:
                subkeys.append(str(self.index_to_word(subkey)))
            new_key = '"' + subkeys[0] + '" and "' + subkeys[1]
            val = str(self.index_to_word(val))
            if self.encoded:
                valid_combs += new_key + " -> " + self.encode(val) + " , "
            else:
                valid_combs += new_key + " -> " + val + " , "
        return valid_combs, len(past_valid_combs)

    def get_valid_combs(self):
        "Returns invalid combinations as a string"
        past_valid_combs = list(self.past_valid_combs.keys())

        return past_valid_combs, len(past_valid_combs)





