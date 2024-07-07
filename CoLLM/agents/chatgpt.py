from CoLLM.agents.base import Agent
import openai
from transformers import AutoTokenizer, AutoModelForCausalLM
from openai import AzureOpenAI



class ChatgptAgent(Agent):


    def __init__(self, forbid_repeats, openended, num_agents, **kwargs):
        super().__init__(**kwargs)
        self.forbit_repeats = forbid_repeats
        self.openended = openended
        self.num_agents = num_agents
        self.setup_llm()

    def load_intro(self):

        if self.num_agents > 1:
            if self.openended:
                filename = "prompts/openended_multi.txt"
            else:
                filename = "prompts/targeted_multi.txt"
        else:
            if self.openended:
                filename = "prompts/openended_single.txt"
            else:
                filename = "prompts/targeted_single.txt"

        temp = open(filename, 'r').readlines()
        intro = " ".join(temp)
        return intro
    def setup_llm(self):


        openai.api_key = None
        if openai.api_key is None:
            print("You need to insert your API token to use chatgpt")

            openai.api_key = str(input('Insert your OpenAI API token: '))

        self.client = AzureOpenAI(
            azure_endpoint="https://eleni.openai.azure.com/",
            api_key=openai.api_key,
            api_version="2024-02-15-preview"
        )

        self.temperature = 1.0

        self.intro = self.load_intro()

    def _get_action(self, state=""):
        # quering openassistant
        messages = [{"role": "system", "content": "You are an intelligent and helpful assistant."}]

        messages.append({"role": "user", "content": self.intro})
        messages.append({"role": "user", "content": state})



        chat = self.client.chat.completions.create(
            model="gpt35",
            messages=messages,
            temperature=self.temperature,
            top_p=1,
        )

        output = chat.choices[0].message.content
        action = self.env.parse_string(output)
        return action
