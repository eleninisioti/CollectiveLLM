"""Little Alchemy 2 Environment containing transition dynamics (lookup dictionary)"""
import json
import collections
import os


class AlchemyEnv:
    
    def __init__(self):
        self.inventory = ["air", "water", "fire", "earth"]
        self.invalid_attempts = []
        
    
    def load_recipe2entity(self, key):
        """
        Loads recipes from the given data file into a dictionary
        mapping Recipe -> resulting entity.
        """
        recipes_path = 'la2/alchemy2.json'
        # Read and parse JSON file
        full_path = os.path.expanduser(recipes_path)
        with open(full_path, 'r') as f:
            data = json.load(f)

        recipe2entity = {}
        for entity, info in data['entities'].items():
            for recipe_data in info['recipes']:
                recipe_key = tuple(sorted(recipe_data))  # make key hashable
                recipe2entity[recipe_key] = entity
        if key in recipe2entity:
            return recipe2entity[key]
        else:
            return ""


    def step(self, step, item1, item2, inventory):
        """ Given two items, check that it is
        in the recipe dictionary"""

        recipe_key = tuple(sorted([item1, item2]))
        result = self.load_recipe2entity(recipe_key)

        if result is None:
            self.invalid_attempts.append(recipe_key)
            
            return f"{item1} + {item2}: invalid combination", None
        elif result in inventory:
            return f"{item1} + {item2} = {result}: {result} already in inventory", result
        else:
            self.inventory.append(result)
            return f"{item1} + {item2} = {result}: {result} is a new item!", result