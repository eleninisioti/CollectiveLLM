""" Defines an abstract interface for an agent.
"""
import os
import numpy as np
import random
import pickle
from source.utils import find_nth
class Agent:
    def __init__(self, idx, project_dir, trial, retry=6):
        """ Constructor of base class.

        Params:
            idx (int): unique ID of agent in the group
            project_dir (str): current project directory for logging dat
            trial (int): current trial in the project (for setting the seed and logging)
            retry (int): number of times a step will be re-attempted

        """
        self.idx = idx
        self.project_dir = project_dir
        self.trial = trial
        self.retry = retry

    def reset_task(self, task, env):
        """ Reset the agent for a new task

        Params:
            task (int): ID of current task
            env (gym environment): environment for current task
        """
        self.env = env
        self.task = task
        self.rewards = 0
        self.success = False
        self.visiting_for = 0
        self.visiting = False
        self.current_log = self.project_dir +  "/logs/trial_" + str(self.trial) + "/task_" + str(self.task)
        self.prev_group = []
        self.past_actions = []
        self.copy_times = {}
        self.invalid_attempts = 0
        np.random.seed(self.trial)
        random.seed(self.trial)

        self.setup_logs()


    def query_until_valid(self, state, current_step):
        """ Query the agent for an action.

        Params:
            state (str): current state of the environment
            current_step (int): index of current step

        """
        self.step = current_step
        output = self.query(state=state, current_step=current_step)
        action, action_str, error = self.parse_action(output)
        self.update_log(action)

        to_not_repeat = []
        failed_attempts = 0

        while len(error) and (failed_attempts < self.retry):
            with open(self.current_log + "/agent_" + str(self.idx) + "/failed.txt", "a") as f:
                f.write("Step " + str(current_step))
                f.write(state)
                f.write("model output is\n" + output)
                f.write("error is \n" + error)

            if "You have already" in error:
                if action_str not in to_not_repeat:
                    to_not_repeat.append(action_str)

            if len(to_not_repeat):
                error = "You have already combined  "
                for el in to_not_repeat:
                    error += el + " , "
                error += "so you should not repeat it. Try another one. "

            new_state = state[:-16] + error + "\n<bot> RESPONSE:\n"
            #new_state = state[:-16] + "\n<bot> RESPONSE:\n"

            with open(self.current_log + "/agent_" + str(self.idx) + "/failed.txt", "a") as f:
                # log the failure

                f.write(new_state)
                f.write("failed " + str(failed_attempts))
                f.write(str(to_not_repeat))

                output = self.query(state=state, current_step=current_step)
                action, action_str, error = self.parse_action(output)
                self.update_log(action)
            failed_attempts += 1
        self.recent_output = output

        if failed_attempts == self.retry:
            failed_step = True
        else:
            failed_step = False
        return action, failed_step



    def parse_action(self, output):
        """ Parse the output of the agent to get the action in the environment.

        Detects errors, such as invalid format, invalid or repeated combinations.

        Params:
            output (str): the output of the agent
        """
        try:
            pos = find_nth(output, "Combination: '", 0)
        except NameError:
            action = None
            action_str = ""
            error = "Invalid output, combination tag nto found.\n"
            return action, action_str, error

        action = None
        action_str = output
        error = ""
        if pos != (-1):
            action_str = action_str[pos:]
            try:
                pos = find_nth(action_str, "Combination: '", 0)
            except NameError:
                action = None
                action_str = ""
                error = "Invalid output, combination tag nto found.\n"
                return action, action_str, error

            pos = pos + len("Combination: '")
            try:
                end_comb = find_nth(action_str, "'", 4)
            except NameError:
                action = None
                action_str = ""
                error = "Invalid output, combination tag nto found.\n"
                return action, action_str, error
            action_str = action_str[(pos - 1):(end_comb + 1)]
            # convert to wordcraft-compatible action
            pos = action_str.find(' and ')
            first_word = action_str[1:(pos - 1)]
            second_word = action_str[(pos + len(' and ') + 1):-1]
            table = self.env.wordcraft_env.table
            if first_word in table and second_word in table:
                action = [int(table.index(first_word)), int(table.index(second_word))]
                action_str = "'" + first_word + "' and '" + second_word + "'"

                if action in self.past_actions:
                    error = "You have already combined  " + first_word + " and " + second_word + " so you cannot repeat it. Try another one. "

            else:
                action = None
                error = "Invalid action, found combination tag but not words. Try again.\n"
        else:
            error = "Invalid action, combination tag not found. Try again.\n"
        return action, action_str, error


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
    def add_info_others(self):
        max_info = 10
        new_state = ""
        if len(self.neighbors):
            new_state += "Other players valid combinations: "
            valid_combs = ""
            counter = 0
            max_info = 15
            filled = False
            total_valid_combs = []
            for agent in self.neighbors:
                if agent.idx != self.idx and not filled:
                    valid_combs, new_combs = agent.env.get_valid_combs()
                    copy_valid_combs = []
                    for el in valid_combs:
                        if el not in total_valid_combs:
                            copy_valid_combs.append(el)
                    total_valid_combs.extend(valid_combs)
                    valid_combs,_ = agent.env.valid_combs_to_string(copy_valid_combs)

                    counter = counter + new_combs

                    if counter > max_info:
                        break
                    new_state += valid_combs

            new_state += "\n Other players invalid combinations (do not repeat combinations here): "
            counter = 0
            total_invalid_combs = []

            for agent in self.neighbors:
                if agent.idx != self.idx:
                    invalid_combs, new_combs = agent.env.get_invalid_combs()

                    copy_invalid_combs = []
                    for el in invalid_combs:
                        if el not in total_invalid_combs:
                            copy_invalid_combs.append(el)
                    total_valid_combs.extend(valid_combs)
                    invalid_combs,_ = agent.env.invalid_combs_to_string(copy_invalid_combs)
                    counter = counter + new_combs

                    if counter > max_info:
                        break
                    new_state += invalid_combs
                    if len(invalid_combs):
                        new_state += ", "

        return new_state


    def parse_action(self, output):
        try:
            pos = find_nth(output, "Combination: '", 0)
        except NameError:
            action = None
            action_str = ""
            error = "Invalid output, combination tag nto found.\n"
            return action, action_str, error

        action = None
        action_str = output
        error = ""
        if pos != (-1):
            action_str = action_str[pos:]
            try:
                pos = find_nth(action_str, "Combination: '", 0)
            except NameError:
                action = None
                action_str = ""
                error = "Invalid output, combination tag nto found.\n"
                return action, action_str, error

            pos = pos + len("Combination: '")
            try:
                end_comb = find_nth(action_str, "'", 4)
            except NameError:
                action = None
                action_str = ""
                error = "Invalid output, combination tag nto found.\n"
                return action, action_str, error
            action_str = action_str[(pos - 1):(end_comb + 1)]
            # convert to wordcraft-compatible action
            pos = action_str.find(' and ')
            first_word = action_str[1:(pos - 1)]
            second_word = action_str[(pos + len(' and ') + 1):-1]
            table = self.env.wordcraft_env.table
            if first_word in table and second_word in table:
                action = [int(table.index(first_word)), int(table.index(second_word))]


                action_str = "'" + first_word + "' and '" + second_word + "'"

                if action in self.past_actions:
                    error = "You have already combined  " + first_word + " and " + second_word + " so you cannot repeat it. Try another one. "


            else:
                action = None
                error = "Invalid action, found combination tag but not words. Try again.\n"
        else:
            error = "Invalid action, combination tag not found. Try again.\n"
        return action, action_str, error


    def compute_copy_time(self, current_step):
        neighbor_elems = []
        for neighb in self.neighbors:
            neighbor_elems.extend(neighb.env.wordcraft_env.env.env.table)
        neighbor_elems = list(set(neighbor_elems))
        for el in neighbor_elems:
            if el in list(self.copy_times.keys()):
                if el in self.env.wordcraft_env.env.env.table and self.copy_times[el][1] is None:
                    self.copy_times[el][1] = current_step - self.copy_times[el][0]
            else:
                if el in self.env.wordcraft_env.env.env.table:
                    self.copy_times[el] = [current_step, 0]

                else:
                    self.copy_times[el] = [current_step, None]


        return self.copy_times


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
        current_log = self.project_dir + "/logs/trial_" + str(self.trial) + "/task_" + str(self.task)
        if not os.path.exists(current_log + "/agent_" + str(self.idx)):
            os.makedirs(current_log + "/agent_" + str(self.idx),exist_ok=True)

        self.count_repeats_valid = 0
        self.count_repeats_invalid = 0
        self.count_double_action = 0
        self.count_repeats_valid_other = 0
        self.count_repeats_invalid_other = 0

    def update_log(self, utterance):
        repeat_valid, repeat_invalid, double_action, repeated_valid_other, repeated_invalid_other = self.analyse_action(
            utterance)
        self.count_repeats_valid += int(repeat_valid)
        self.count_repeats_invalid += int(repeat_invalid)
        self.count_double_action += int(double_action)
        self.count_repeats_valid_other += int(repeated_valid_other)
        self.count_repeats_invalid_other += int(repeated_invalid_other)

    def wrapup_task(self):
        # save current task general info
        with open(self.current_log + "/agent_" + str(self.idx) + "/dialogue.txt", "a") as f:
            f.write("Task " + str(self.task) + " ended with success " + str(self.success) + " steps " + str(self.step) )

        with open(self.current_log + "/agent_" + str(self.idx) + "/copy_time_info.pkl", "wb") as f:
            pickle.dump(self.copy_times, f)

    def write_log(self, state):
        with open(self.current_log + "/agent_" + str(self.idx) + "/dialogue.txt", "a") as f:
            f.write(state + self.recent_output)
    # --------------------------------------------------
