""" Defines a group of agents solving a Wordcraft task.
"""
from source.agents.baseline_single import RandomAgent, EmpowerAgent
from source.agents.LLM_agents import ChatgptAgent, OllamaAgent
import random


class Group:

    def __init__(self, num_agents, agent_type, connectivity, visit_prob, visit_duration, openended, project_dir, trial,
                 forbid_repeats, temperature, top_p, env_config):
        self.num_agents = num_agents
        self.connectivity = connectivity
        self.visit_prob = visit_prob
        self.visit_duration = visit_duration
        self.openended = openended
        self.project_dir = project_dir
        self.trial = trial
        self.agent_type = agent_type
        self.forbid_repeats = forbid_repeats
        self.visit_log = self.project_dir + "/visit_log.txt"
        self.visit_duration = visit_duration
        self.visit_prob = visit_prob
        self.temperature = temperature
        self.top_p = top_p

        self.env_config = env_config

        self._init_agents()

    def _init_agents(self):
        self.agents = []
        for agent_idx in range(self.num_agents):

            if self.agent_type == "random":
                new_agent = RandomAgent(
                    idx=agent_idx,
                    project_dir=self.project_dir,
                    trial=self.trial,
                    forbid_repeats=self.forbid_repeats,
                    env_config=self.env_config)

            elif self.agent_type == "empower":
                new_agent = EmpowerAgent(idx=agent_idx,
                                         project_dir=self.project_dir,
                                         trial=self.trial,
                                         env_config=self.env_config)


            elif self.agent_type == "chatgpt":
                new_agent = ChatgptAgent(idx=agent_idx,
                                         project_dir=self.project_dir,
                                         trial=self.trial,
                                         openended=self.openended,
                                         num_agents=self.num_agents)

            elif self.agent_type in ["llama3", "llama2"]:
                new_agent = OllamaAgent(idx=agent_idx,
                                        agent_type=self.agent_type,
                                        project_dir=self.project_dir,
                                        trial=self.trial,
                                        openended=self.openended,
                                        num_agents=self.num_agents)

            self.agents.append(new_agent)

        self.determine_neighbors()

    def reset_task(self, task):
        # create environments for all agents
        self.task = task
        for idx, agent in enumerate(self.agents):
            agent.reset_task(task)

    def step(self, current_step):
        if self.connectivity == "dynamic" and len(self.agents) > 2:
            # a visit takes place with chosen probability
            self.visit(current_step)

        group_results = []

        for agent in self.agents:

            if not agent.success:
                # get current environmental state
                state = agent.env.render(agent.get_neighbor_envs())

                repeat = True

                while repeat:
                    action, items = agent.move(state)
                    obs, reward, done, info = agent.env.step(action)
                    repeat = info["repeat"]

                # act in the environment
                agent.past_actions.append(items)

                if done and reward:
                    agent.success = True
                    agent.step_solved = current_step

                agent.log_step(step=current_step,obs=state, action=items)

                group_results.append([self.trial,
                                      self.task,
                                      agent.idx,
                                      current_step,
                                      agent.success,
                                      agent.step_solved,
                                      items,
                                      len(agent.env.get_inventory())])
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

    def visit(self, current_step):
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
                to_visit = random.choice(
                    [pot for pot in self.agents if (pot != agent) and (pot not in agent.prev_group)])
                with open(self.visit_log, "a") as f:
                    f.write(" he is visiting " + str(to_visit.idx))

                agent.neighbors.append(to_visit)
                for neighb in to_visit.neighbors:
                    neighb.neighbors.append(agent)
                    agent.neighbors.append(neighb)
                to_visit.neighbors.append(agent)
