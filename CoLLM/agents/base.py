""" Defines an abstract interface for an agent.
"""
import os
import numpy as np
import random
import pickle
from CoLLM.utils import find_nth
import os


class Agent:
    def __init__(self, idx, num_steps, project_dir, trial, env, active_memory_capacity=None, memory_type=None):
        """ Constructor of base class.

        Params:
            idx (int): unique ID of agent in the group
            project_dir (str): directory for logging agent-specific data
            trial (int): current trial in the project (for setting the seed and logging)
            retry (int): number of times a step will be re-attempted

        """
        self.idx = idx
        self.project_dir = project_dir
        self.trial = trial
        self.env = env
        self.num_steps = num_steps
        self.memory_type=memory_type
        self.active_memory_capacity=active_memory_capacity
        
        self.forbid_repeats = False
        self.invalid_actions = 0
        self.rank = None
        self.memory = {}
        self.active_memory = []
        
        
    def render(self):
        pass


    def reset_task(self, task):
        """ Reset the agent for a new task

        Params:
            task (int): ID of current task
            env (gym environment): environment for current task
        """


        self.task = task
        self.rewards = 0
        self.success = False
        self.visiting_for = 0
        self.visiting = False
        self.current_log = self.project_dir + "/logs/trial_" + str(self.trial) + "/task_" + str(self.task) + "/agent_" + str(self.idx)
        self.prev_group = []
        self.copy_times = {}
        self.invalid_attempts = 0
        self.step_solved = None
        np.random.seed(self.trial)
        random.seed(self.trial)

        self.setup_logs()


    def get_social_inventory(self):
        social_inventory = []
        for neighbor in self.neighbors:
            social_inventory.extend(neighbor.env.inventory)
        return social_inventory

    def move(self):
        
        memory = self.fetch_memory(self.env.inventory)

        action, output, inventory = self._get_action(memory)
        counter = 0
        if self.forbid_repeats:
            already_played = action in self.past_actions

            while already_played and counter < 20:
                action, output = self._get_action()
                already_played = action in self.past_actions
                counter += 1

        output = "Combination: '" + action[0] + "' and '" + action[1] + "'"

        return output, action, inventory



    def get_neighbor_envs(self):
        return [neighb.env for neighb in self.neighbors]


    def analyse_action(self, action_str):
        """ Analyses an action to check whether it represetnes a repeated combination (valid or invalid, by the agent itself or
        one of its neighbors).
        """
        other_valid = []
        other_invalid = []
        for agent in self.neighbors:
            if agent.idx != self.idx:
                invalid_combs, _ = agent.env.get_invalid_combs()
                other_invalid.extend(invalid_combs)
                valid_combs, _ = agent.env.get_valid_combs()
                other_valid.extend(valid_combs)
        other_invalid = list(set(other_invalid))
        other_valid = list(set(other_valid))

        repeated_valid = False
        repeated_invalid = False
        repeated_valid_other = False
        repeated_invalid_other = False
        if action_str is not None:
            action_str = tuple(action_str)

            if action_str in list(self.env.past_valid_combs.keys()):
                repeated_valid = True

            if action_str in self.env.past_invalid_combs:
                repeated_invalid = True

            if action_str in other_valid:
                repeated_valid_other = True

            if action_str in other_invalid:
                repeated_invalid_other = True

        double_item = False
        action = action_str
        if action is not None:
            if action not in self.env.past_invalid_combs and action not in list(self.env.past_valid_combs.keys()):

                if action[0] == action[1]:
                    double_item = True

        return repeated_valid, repeated_invalid, double_item, repeated_valid_other, repeated_invalid_other

    def return_to_group(self, agents):
        """ An agent returns to its original group
        """
        self.neighbors = []
        for agent in agents:
            if self in agent.neighbors:
                agent.neighbors.remove(self)
        for agent in self.prev_group:
            agent.neighbors.append(self)
            self.neighbors.append(agent)
        self.visiting = False
        self.visiting_for = 0
        return agents

    # ----- logging utilities -----
    def setup_logs(self):
        if not os.path.exists(self.current_log):
            os.makedirs(self.current_log , exist_ok=True)

        self.count_repeats_valid = 0
        self.count_repeats_invalid = 0
        self.count_double_action = 0
        self.count_repeats_valid_other = 0
        self.count_repeats_invalid_other = 0
        
        
        
    def rank_memory_relevance(self, memory, info):
        instructions = "You are currently playing a game. In this game I give you an inventory of items that you need to combine in pairs to make new items."
        instructions += "I will give you some information that has the form item1 and item2 -> output), where item1 and item2 can be combined to make output. "
        instructions += "If output is 'Nothing', this means that this combination does not give a new item. "
        instructions += "I want you to give me a value between 0 and 1 that characterizes how relevant this information is based on your current inventory"
        instructions += "An information is relevant if it is likely to help play the gema. For example, it can help you produce an item that you don't have or avoid attempting an item that is invalid or that you have already tried."
        
        if memory[2]:  # result exists and is not None/empty
            memory_str = f"'{memory[0]}' and '{memory[1]}' -> '{memory[2]}'"
        else:
            memory_str = f"'{memory[0]}' and '{memory[1]}' -> Nothing "
        content = instructions + "\n Here is the inventory: " + info + "\n Here is the information: " + memory_str  + "\n The relevance is (just give me a number between 0 and 1): "
        relevance = self.prompt(content)
        relevance = self.postprocess_relevance(relevance)
        
        return relevance    

            
    
    def rank_memory(self, memory, info):
        # relevance, recency, importance
        
        if self.memory_type == "recency":
            recency = memory[3]/self.num_steps
            rank = recency
        elif self.memory_type == "relevance":
            relevance = self.rank_memory_relevance(memory, info)
            rank = relevance
          
        elif self.memory_type == "mix":
            recency = memory[3]/self.num_steps
            relevance = self.rank_memory_relevance(memory, info)
            rank = recency + relevance
                        
        return rank
        
        
        
    def fetch_memory(self, info):
        
        if self.memory_type != None:
            # we check if the info is in the memory
            
            if len(self.memory) > self.active_memory_capacity:

            
                if self.memory_type == "random":
                    active_memory = random.choices(list(self.memory.keys()), k=self.active_memory_capacity)
                    active_memory = [list(memory) + [self.memory[memory]] for memory in active_memory]

                else:
                    ranks = []
                    for memory_key, memory_value in self.memory.items():
                        memory = list(memory_key) + [memory_value]
                        rank = self.rank_memory(memory, info)
                        ranks.append(rank)

                    # Pair each memory with its rank
                    memory_rank_pairs = list(zip(self.memory, ranks))
                    # Sort by rank descending (assuming higher rank is better)
                    memory_rank_pairs.sort(key=lambda x: x[1], reverse=True)
                    # Take the top max_memories
                    top_memories = memory_rank_pairs[:self.active_memory_capacity]
                    # Extract just the memory part
                    active_memory = [list(mem) + [self.memory[mem]] for mem, _ in top_memories]
                    self.rank = ranks
            else:
                active_memory = list(self.memory.keys())
                active_memory = [list(memory) + [self.memory[memory]] for memory in active_memory]
                
            
            memory_str = "Past valid combinations:\n"
            valid_combos = []
            invalid_combos = []

            for mem in active_memory:
                # Assuming mem is a tuple like (item1, item2, result)
                if  mem[2]:  # result exists and is not None/empty
                    valid_combos.append(f"'{mem[0]}' and '{mem[1]}' -> '{mem[2]}'")
                else:
                    invalid_combos.append(f"'{mem[0]}' and '{mem[1]}'")

            memory_str += "\n".join(valid_combos)
            memory_str += "\nPast invalid combinations:\n"
            memory_str += "\n".join(invalid_combos)
            
            self.active_memory = active_memory
        else:
            memory_str = ""

        return memory_str


    def log_step(self, step, inventory, obs, action, memory):
        with open(self.current_log + "/game.txt", "a") as f:
            f.write("Step " + str(step)+ "\n")
            f.write("Inventory: " + str(inventory) + "\n")
            f.write("Memory: " + str(inventory) + "\n")
            f.write("Observation: " + obs + "\n")
            f.write("Agent output: \n" + str(action) + "\n \n")



    def wrapup_task(self):
        # save current task general info
        with open(self.current_log + "/game.txt", "a") as f:
            f.write("Task " + str(self.task) + " ended with success " + str(self.success) + " at step " + str(self.step_solved))
            
        with open(self.current_log + "/game_info.pkl", "wb") as f:
            pickle.dump({"inventory": self.env.inventory, 
                         "valid_attempts": self.env.valid_attempts,
                        "repeats_valid": self.env.repeats_valid,
                        "invalid_attempts": self.env.invalid_attempts,
                         "repeats_invalid": self.env.repeats_invalid,
                         }, f)
