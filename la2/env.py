"""Little Alchemy 2 Environment containing transition dynamics (lookup dictionary)"""
import json
import collections
import os


class AlchemyEnv:
    
    def __init__(self):
        self.inventory = ["air", "water", "fire", "earth"]
        self.invalid_attempts = []
        self.valid_attempts = []
        self.repeats_valid = 0
        self.repeats_invalid = 0
        
    
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


    def step(self, step, item1, item2):
        """ Given two items, check that it is
        in the recipe dictionary"""
        
        inventory = self.inventory

        recipe_key = tuple(sorted([item1, item2]))
        result = self.load_recipe2entity(recipe_key)
        
        print(recipe_key)
        
        # Convert recipe_key set to both possible permutations
        recipe_list = list(recipe_key)
        recipe_perm1 = (recipe_list[0], recipe_list[1])
        recipe_perm2 = (recipe_list[1], recipe_list[0])
        
        if recipe_perm1 in self.valid_attempts or recipe_perm2 in self.valid_attempts:
            print(recipe_key, "valid", step)
            self.repeats_valid += 1
        if recipe_perm1 in self.invalid_attempts or recipe_perm2 in self.invalid_attempts:
            print(recipe_key, "invalid", step)

            self.repeats_invalid += 1


        if not len(result):
            if recipe_key not in self.invalid_attempts:
                self.invalid_attempts.append(recipe_key)    
                
        else:
            if recipe_key not in self.valid_attempts:
                self.valid_attempts.append(recipe_key)
                
        if not len(result):
            return f"{item1} + {item2}: invalid combination", result
        elif result in inventory:
            return f"{item1} + {item2} = {result}: {result} already in inventory", result
        else:
            self.inventory.append(result)
            return f"{item1} + {item2} = {result}: {result} is a new item!", result
        
                

            
            
            
            
            