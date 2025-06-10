""" Defines an abstract interface for an agent.
"""
import os
import numpy as np
import random
import pickle
from CoLLM.utils import find_nth
import os


class Agent:
    def __init__(self, idx, project_dir, trial, env):
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
        self.has_memory = False
        
        self.invalid_actions = 0
        self.rank = None
        self.memory = []
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



    def move(self):

        action, output = self._get_action()
        counter = 0
        if self.forbid_repeats:
            already_played = action in self.past_actions

            while already_played and counter < 20:
                action, output = self._get_action()
                already_played = action in self.past_actions
                counter += 1

        output = "Combination: '" + action[0] + "' and '" + action[1] + "'"

        return output, action



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


    def log_step(self, step, obs, action, repeat):
        with open(self.current_log + "/game.txt", "a") as f:
            f.write("Step " + str(step)+ "\n")
            f.write("Observation: " + obs + "\n")
            f.write("Agent output: \n" + str(action) + "\n \n")
            f.write("Repetiton" + str(repeat))



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
