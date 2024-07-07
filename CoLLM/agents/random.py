
from CoLLM.agents.base import Agent
import numpy as np


class RandomAgent(Agent):
    """ Chooses two random items from the inventory.
    """
    def __init__(self, seed=0, forbid_repeats=False,  **kwargs):
        """ Class constructor

        Args:
            forbit_repeats (bool): if True, random combinations are always novel in the current task

        """
        self.forbid_repeats = forbid_repeats

        np.random.seed(seed)
        super().__init__(**kwargs)

    def _get_action(self, state):
        inventory = self.env.get_inventory()

        random_loc = np.random.randint(0, len(inventory))
        random_word1 = inventory[random_loc]
        random_loc = np.random.randint(0, len(inventory))
        random_word2 = inventory[random_loc]

        action = random_word1, random_word2

        return action