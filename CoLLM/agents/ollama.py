""" An LLM player is provided with a prompt describing the task and the current state of the environment.
"""

import ollama
from CoLLM.agents.base import Agent

class OllamaAgent(Agent):

    def __init__(self, seed, targeted, multiagent, forbid_repeats=False,**kwargs):
        self.forbid_repeats = forbid_repeats
        self.seed = seed

        super().__init__(**kwargs)
        self.setup(targeted, multiagent)

    def setup(self, targeted, multiagent):
        if targeted and multiagent:
            prompt_file = self.env.env_dir + "/prompts/targeted_multi.txt"
        elif targeted and not multiagent:
            prompt_file = self.env.env_dir + "/prompts/openended_multi.txt"
        elif not targeted and multiagent:
            prompt_file = self.env.env_dir + "/prompts/openended_multi.txt"
        else:
            prompt_file = self.env.env_dir + "/prompts/openended_single.txt"

        temp = open(prompt_file, 'r').readlines()
        self.intro = " ".join(temp)

    def _get_action(self, state):

        state = self.intro + "\n<bot> RESPONSE:\n" + state

        response = ollama.chat(model='llama3', messages=[
            {
                'role': 'user',
                'content': state,
            },
        ])
        response = response['message']['content']
        action = self.env.parse_input(response)

        return action
