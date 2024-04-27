from structured_multi_LLM.base_agent import Agent
from structured_multi_LLM.baseline_agents import RandomAgent, UncertaintyAgent, EmpowerAgent, EmpowerOnestepAgent, NoisyEmpowerAgent, Noisyv2EmpowerAgent, CulturalEvolutionAgent, EmpowerCulturalEvolutionAgent
from structured_multi_LLM.LLM_agents import OAAgent, ChatgptAgent, ChatgptCulturalevoAgent, LLama2Agent, LLama2AgentWithCopy
import random
import numpy as np
from itertools import combinations
from wordcraft_openended.recipe_book import (Recipe)
class Group:

    def __init__(self, num_agents, model_name, connectivity, visit_prob, visit_duration, openended, project_dir, trial, forbid_repeats, temperature, top_p):
        self.num_agents = num_agents
        self.connectivity = connectivity
        self.visit_prob = visit_prob
        self.visit_duration = visit_duration
        self.openended = openended
        self.project_dir = project_dir
        self.trial = trial
        self.model_name = model_name
        self.forbid_repeats = forbid_repeats
        self.visit_log = self.project_dir + "/visit_log.txt"
        self.visit_duration = visit_duration
        self.visit_prob = visit_prob
        self.temperature = temperature
        self.top_p = top_p

        self._init_agents()

    def _init_agents(self):
        self.agents = []
        for agent_idx in range(self.num_agents):

            if self.model_name == "random":
                new_agent = RandomAgent(
                          idx=agent_idx,
                                project_dir=self.project_dir,
                                trial=self.trial,
                forbid_repeats=self.forbid_repeats)


            elif self.model_name == "uncertainty":
                new_agent = UncertaintyAgent(idx=agent_idx,
                                project_dir=self.project_dir,
                                trial=self.trial,
                forbid_repeats=self.forbid_repeats)
            elif self.model_name == "cultural_evo":
                new_agent = CulturalEvolutionAgent(idx=agent_idx,
                                project_dir=self.project_dir,
                                trial=self.trial,
                forbid_repeats=self.forbid_repeats)
            elif self.model_name == "empower_cultural_evo":
                new_agent = EmpowerCulturalEvolutionAgent(idx=agent_idx,
                                project_dir=self.project_dir,
                                trial=self.trial,
                forbid_repeats=self.forbid_repeats)
            elif self.model_name == "empower":
                new_agent = EmpowerAgent(idx=agent_idx,
                                            project_dir=self.project_dir,
                                            trial=self.trial,
                forbid_repeats=self.forbid_repeats)

            elif self.model_name == "noisy_empower":
                new_agent = NoisyEmpowerAgent(idx=agent_idx,
                                            project_dir=self.project_dir,
                                            trial=self.trial,
                forbid_repeats=self.forbid_repeats)
            elif self.model_name == "noisyv2_empower":
                new_agent = Noisyv2EmpowerAgent(idx=agent_idx,
                                              project_dir=self.project_dir,
                                              trial=self.trial,
                                              forbid_repeats=self.forbid_repeats)
            elif self.model_name == "empower_onestep":
                new_agent = EmpowerOnestepAgent(idx=agent_idx,
                                project_dir=self.project_dir,
                                trial=self.trial,
                forbid_repeats=self.forbid_repeats)
            elif self.model_name == "chatgpt":
                new_agent = ChatgptAgent(idx=agent_idx,
                                project_dir=self.project_dir,
                                trial=self.trial,
                                         openended=self.openended,
                                         num_agents=self.num_agents)

            elif self.model_name == "chatgpt_cultural_evo":
                new_agent = ChatgptCulturalevoAgent(idx=agent_idx,
                                project_dir=self.project_dir,
                                trial=self.trial,
                                         openended=self.openended,
                                         num_agents=self.num_agents)

            elif self.model_name == "OA":
                new_agent = OAAgent(idx=agent_idx,
                                project_dir=self.project_dir,
                                trial=self.trial,
                                         openended=self.openended,
                                         num_agents=self.num_agents)


            elif self.model_name == "llama2":
                new_agent = LLama2Agent(idx=agent_idx,
                                project_dir=self.project_dir,
                                trial=self.trial,
                                         openended=self.openended,
                                         num_agents=self.num_agents,
                                        temperature=self.temperature,
                                        top_p=self.top_p)


            elif self.model_name == "llama2_copy":
                new_agent = LLama2AgentWithCopy(idx=agent_idx,
                                project_dir=self.project_dir,
                                trial=self.trial,
                                         openended=self.openended,
                                         num_agents=self.num_agents,
                                        temperature=self.temperature,
                                        top_p=self.top_p)




            self.agents.append(new_agent)

        #self.agents.append(new_agent)
        self.determine_neighbors()





    def reset_task(self, task, envs):
        # create environments for all agents
        self.task = task
        self.envs = envs
        for idx, agent in enumerate(self.agents):
            agent.reset_task(task, self.envs[idx])

    def step(self, current_step):
        if self.connectivity == "dynamic" and len(self.agents) > 2:
            # a visit takes place with chosen probability
            self.visit( current_step)

        group_results = []

        for agent in self.agents:

            if not agent.success:
                # get current environmental state
                state = agent.env.render()
                info_others = agent.add_info_others()
                state = state + "\n" + info_others+ "\n<bot> RESPONSE\n"
                print("SStep ",current_step)
                print(state)

                action, failed_step = agent.query_until_valid(state=state, current_step=current_step)
                print(action, failed_step)

                if failed_step:
                    # register that the agent did not act in this step
                    agent.invalid_attempts += 1
                else:
                    # act in the environment
                    agent.past_actions.append(action)
                    obs, reward, done, info = agent.env.step(action)
                    agent.rewards += reward

                    agent.write_log(state)

                    if done and reward:
                        agent.success = True
                        agent.step = current_step

            inventory = agent.env.wordcraft_env.env.env.table
            if agent.success:
                action_store = ""
                action_words = ""
            else:
                if len(agent.past_actions):
                    action_store = str(agent.past_actions[-1][0]) + ' ' + str(agent.past_actions[-1][1])
                    action_words = inventory[agent.past_actions[-1][0]] + ' ' + inventory[agent.past_actions[-1][1]]
                else:
                    action_store = ""
                    action_words = ""

            # log step to results
            copy_time = agent.compute_copy_time(current_step)
            time_copied = [el[1] for el in copy_time.values() if el[1] is not None]
            copy_time = np.mean(time_copied)
            print(copy_time)

            # perc of explored space
            possible_combs = list(combinations(agent.env.wordcraft_env.env.table, 2))
            tuple_of_tuples = tuple(tuple(sublist) for sublist in agent.past_actions)

            # Use set to get unique sublists
            unique_actions = list(set(tuple_of_tuples))

            perc_explore = len(unique_actions)/len(possible_combs)

            # perc of meaningful explored space
            recipes = [Recipe(el) for el in possible_combs]
            results = [ agent.env.wordcraft_env.recipe_book.evaluate_recipe(recipe) for recipe in recipes]
            results = [x for x in results if x is not None]
            results.extend(agent.env.wordcraft_env.env.table)
            results = list(set(results))
            meaningful_space_size = len(list(set(results)))

            meaningful_actions = len(agent.env.wordcraft_env.env.table)

            perc_explore_meaning = meaningful_actions / meaningful_space_size

            print("step " + str(agent.step) + " inventory length:" + str(len(agent.env.wordcraft_env.env.table)))

            group_results.append([self.trial,
             self.task,
             agent.idx,
             agent.success,
             agent.step,
             agent.count_repeats_valid,
             agent.count_repeats_invalid,
             agent.count_double_action,
             agent.count_repeats_valid_other,
             agent.count_repeats_invalid_other,
             agent.rewards,
             current_step,
             action_store,
             action_words,
             agent.invalid_attempts,
             len(agent.env.wordcraft_env.env.table),
             copy_time,
             perc_explore,
            perc_explore_meaning])
        return group_results

    def wrap_up(self):
        for agent in self.agents:
            agent.wrapup_task()



    def determine_neighbors(self):
        for agent in self.agents:
            if len(self.agents) > 1:
                if self.connectivity == "fully-connected":
                    neighbors = [self.agents[el] for el in range(len(self.agents)) if el != agent.idx]
                elif self.connectivity == "dynamic":
                    pairs = [[el, el + 1] for el in range(0, len(self.agents), 2)]
                    for pair in pairs:
                        if agent.idx in pair:
                            neighbors = [self.agents[el] for el in pair if el != agent.idx]
                            break
            else:
                neighbors = []

            agent.neighbors = neighbors

    def visit(self,   current_step):
        random.shuffle(self.agents)
        with open(self.visit_log, "a") as f:
            for agent in self.agents:
                for neighbor in agent.neighbors:
                    f.write(
                        "At step " + str(current_step) + " agent " + str(agent.idx) + " has neighbor " + str(
                            neighbor.idx) + "\n")
        # update all visiting agents
        for agent in self.agents:
            if agent.visiting:
                agent.visiting_for += 1

        # is there someone returning from a visit?
        for agent in self.agents:
            if agent.visiting_for == self.visit_duration:
                with open(self.visit_log, "a") as f:
                    f.write("agent " + str(agent.idx) + " returning")
                    self.agents = agent.return_to_group(self.agents)
        # is there a new visit
        for agent in self.agents:
            small_number = random.uniform(0, 1)
            if (small_number < self.visit_prob) and (not sum([x.visiting for x in self.agents])):
                with open(self.visit_log, "a") as f:
                    f.write(" visiting agent is " + str(agent.idx))
                agent.visiting = True
                agent.visiting_for = 0
                agent.prev_group = agent.neighbors[:]
                for neighb in agent.prev_group:
                    neighb.neighbors.remove(agent)
                    agent.neighbors.remove(neighb)
                # pick agent to visit
                to_visit = random.choice([pot for pot in self.agents if (pot != agent) and (pot not in agent.prev_group)])
                with open(self.visit_log, "a") as f:
                    f.write(" he is visiting " + str(to_visit.idx))

                agent.neighbors.append(to_visit)
                for neighb in to_visit.neighbors:
                    neighb.neighbors.append(agent)
                    agent.neighbors.append(neighb)
                to_visit.neighbors.append(agent)

