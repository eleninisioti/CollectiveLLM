""" Defines a group of agents solving a Wordcraft task.
"""
from CoLLM.agents import *
import random
import copy
import wandb

class Group:

    def __init__(self, seed, num_agents, agent_type, connectivity, visit_prob, visit_duration, openended, project_dir, trial,
                 forbid_repeats, temperature, top_p, env, memory_type, num_steps, active_memory_capacity, prob_artifact_disappear):
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
        self.seed = seed
        self.memory_type = memory_type  
        self.num_steps = num_steps
        self.envs = [copy.deepcopy(env) for _ in range(self.num_agents)]
        self.prob_artifact_disappear = prob_artifact_disappear
        self.active_memory_capacity = active_memory_capacity

        self._init_agents()

    def _init_agents(self):

        if self.agent_type in ["llama3", "llama2"]:
            import subprocess
            print("Pulling ollama agent")
            subprocess.run(['ollama', 'pull', self.agent_type], capture_output=True, text=True)
        self.agents = []
        for agent_idx in range(self.num_agents):

            if self.agent_type == "random":
                new_agent = RandomAgent(
                    seed=self.seed,
                    idx=agent_idx,
                    num_steps=self.num_steps,
                    project_dir=self.project_dir,
                    trial=self.trial,
                    env=self.envs[agent_idx],
                    memory_type=self.memory_type,
                   active_memory_capacity=self.active_memory_capacity,
)

            elif self.agent_type == "empower":
                new_agent = EmpowerAgent(
                    idx=agent_idx,
                    num_steps=self.num_steps,
                    project_dir=self.project_dir,
                    trial=self.trial,
                    env=self.envs[agent_idx],
                    memory_type=self.memory_type,
                   active_memory_capacity=self.active_memory_capacity,)


            elif self.agent_type == "openai":
                new_agent = OpenAIAgent(idx=agent_idx,
                                         project_dir=self.project_dir,
                                         forbid_repeats=False,
                                         trial=self.trial,
                                         openended=self.openended,
                                         num_agents=self.num_agents,
                                         env=self.envs[agent_idx])

            elif self.agent_type == "ollama":
                new_agent = OllamaAgent(seed=self.seed,
                                        idx=agent_idx,
                                        project_dir=self.project_dir,
                                        trial=self.trial,
                                        multiagent=(self.num_agents-1),
                                        env=self.envs[agent_idx],
                                        memory_type=self.memory_type,
                                        active_memory_capacity=self.active_memory_capacity,
                                        )
            elif self.agent_type == "gemini":
                new_agent = GeminiAgent(seed=self.seed,
                                        idx=agent_idx,
                                        project_dir=self.project_dir,
                                        trial=self.trial,
                                        multiagent=(self.num_agents-1),
                                        env=self.envs[agent_idx],
                                        num_steps=self.num_steps,
                                        memory_type=self.memory_type,
                                        active_memory_capacity=self.active_memory_capacity,
                                        )

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
        log_info = {"inventory":{"agent_" + str(el): [] for el in range(len(self.agents))},
                    "memory": {"agent_" + str(el): [] for el in range(len(self.agents))},
                    "active_memory": {"agent_" + str(el): [] for el in range(len(self.agents))},
                    "actions": {"agent_" + str(el): [] for el in range(len(self.agents))},
                    "rank": {"agent_" + str(el): [] for el in range(len(self.agents))},
                    "valid_attempts": {"agent_" + str(el): [] for el in range(len(self.agents))},
                    "invalid_attempts": {"agent_" + str(el): [] for el in range(len(self.agents))}
                    }

        for agent in self.agents:

            if not agent.success:
                # get current environmental state

                action, items, inventory = agent.move()
                message, obs = agent.env.step(current_step, items[0], items[1], inventory)

                if agent.memory_type != None:
                    agent.memory[(items[0], items[1], obs)] = current_step
                                    
                agent.log_step(step=current_step, obs=obs, action=action, inventory=agent.env.inventory, memory=agent.active_memory)
                

                # artifact may disappear from an agent's inventory
                if random.uniform(0, 1) < self.prob_artifact_disappear:
                    # pick a random artifact from the inventory
                    if len(agent.env.inventory) > 2:
                        artifact = random.choice(agent.env.inventory)
                        agent.env.inventory.remove(artifact)
                    
                log_info["inventory"]["agent_" + str(agent.idx)] =  agent.env.inventory
                log_info["memory"]["agent_" + str(agent.idx)] = agent.memory
                log_info["active_memory"]["agent_" + str(agent.idx)] = agent.active_memory
                log_info["actions"]["agent_" + str(agent.idx)] = items
                log_info["rank"]["agent_" + str(agent.idx)] = agent.rank
                log_info["valid_attempts"]["agent_" + str(agent.idx)] = agent.env.valid_attempts
                log_info["invalid_attempts"]["agent_" + str(agent.idx)] = agent.env.invalid_attempts    
                
                print("agent ", agent.idx, "inventory", len(agent.env.inventory))
                group_results.append([self.trial,
                                      self.task,
                                      agent.idx,
                                      current_step,
                                      agent.env.repeats_valid,
                                      agent.env.repeats_invalid,
                                      len(agent.env.invalid_attempts),
                                      agent.invalid_actions,
                                      len(agent.env.inventory)])
                
        # Flatten the list of lists and count unique elements
        group_inventory = [item for agent in self.agents for item in agent.env.inventory]
        unique_count = len(set(group_inventory))
        
        wandb.log({"mean_inventory_size": unique_count})
        
        # Add group_inventory to the end of each list in group_results
        for i, result in enumerate(group_results):
            group_results[i] = result + [unique_count]
        
        return group_results, log_info

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
                
        visit_on = sum([1 for agent in self.agents if agent.visiting])

        # is there someone returning from a visit?
        for agent in self.agents:
            if agent.visiting_for == self.visit_duration:
                with open(self.visit_log, "a") as f:
                    f.write("agent " + str(agent.idx) + " returning")
                    self.agents = agent.return_to_group(self.agents)
        # is there a new visit
        for agent in self.agents:
            small_number = random.uniform(0, 1)
            if (small_number < self.visit_prob) and not visit_on:
                with open(self.visit_log, "a") as f:
                    f.write(" visiting agent is " + str(agent.idx))
                # pick agent to visit
                potential_visitors = [pot for pot in self.agents if (pot != agent) and (pot not in agent.prev_group)]
                if len(potential_visitors) > 0:
                    agent.visiting = True
                    agent.visiting_for = 0
                    agent.prev_group = agent.neighbors[:]
                    for neighb in agent.prev_group:
                        neighb.neighbors.remove(agent)
                        agent.neighbors.remove(neighb)
                    
                    to_visit = random.choice(potential_visitors)
                        
                    with open(self.visit_log, "a") as f:
                        f.write(" he is visiting " + str(to_visit.idx))

                    agent.neighbors.append(to_visit)
                    for neighb in to_visit.neighbors:
                        neighb.neighbors.append(agent)
                        agent.neighbors.append(neighb)
                    to_visit.neighbors.append(agent)

                else:
                    continue
                    

