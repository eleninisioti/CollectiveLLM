from CoLLM.agents.base import Agent
from CoLLM.utils import softmax_with_temperature




class EmpowerAgent(Agent):

    def __init__(self, **kwargs):
        self.forbid_repeats = True # this agent is deterministic so it won't work if we don't forbid repeats
        super().__init__(**kwargs)

    def _get_action(self):
        recipes = self.env.recipe_book.entity2recipes
        all_combs = []
        for el1 in self.env.table:
            for el2 in self.env.table:
                if [el2, el1] not in all_combs and [el1, el2] not in all_combs:
                    if [el1, el2] not in self.past_actions:
                        all_combs.append([el1, el2])

        empower_values = []
        for comb in all_combs:

            recipe = self.env.Recipe(comb)
            new_el = self.env.recipe_book.evaluate_recipe(recipe)
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

        action = [first_word, second_word]

        return action
