from structured_multi_LLM.base_agent import Agent
import openai
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List, Optional
import fire
from llama import Llama, Dialog
from openai import AzureOpenAI
import os
class LLama2Agent(Agent):
    def __init__(self, openended, num_agents, temperature, top_p, **kwargs):
        super().__init__(**kwargs)
        self.openended = openended
        self.num_agents = num_agents
        self.temperature = temperature
        self.top_p = top_p
        self.setup_llm()

    def load_intro(self):

        if self.num_agents > 1:
            if self.openended:
                filename = "prompts/openended_multi.txt"
            else:
                filename = "prompts/targeted_multi.txt"
        else:
            if self.openended:
                filename = "prompts/openended_single_noinfo.txt"
            else:
                filename = "prompts/targeted_single.txt"

        temp = open(filename, 'r').readlines()
        intro = " ".join(temp)
        return intro

    def setup_llm(self):
        ckpt_dir = "/gpfsscratch/rech/imi/utw61ti/llama3/Meta-Llama-3-8B-Instruct"
        tokenizer_path = "/gpfsscratch/rech/imi/utw61ti/llama3/Meta-Llama-3-8B-Instruct/tokenizer.model"
        ckpt_dir = "/gpfsscratch/rech/imi/utw61ti/llama3/Meta-Llama-3-8B"
        tokenizer_path = "/gpfsscratch/rech/imi/utw61ti/llama3/Meta-Llama-3-8B/tokenizer.model"
        ckpt_dir = "/gpfsscratch/rech/imi/utw61ti/llama3/Meta-Llama-3-70B"
        tokenizer_path = "/gpfsscratch/rech/imi/utw61ti/llama3/Meta-Llama-3-70B/tokenizer.model"
        self.max_seq_len =2200
        self.max_batch_size = 8
        #self.temperature = 1.0
        #self.top_p = 0.9
        self.max_gen_len =None
        self.generator = Llama.build(
            ckpt_dir=ckpt_dir,
            tokenizer_path=tokenizer_path,
            max_seq_len=self.max_seq_len,
            max_batch_size=self.max_batch_size,
            #model_parallel_size=8
        )
        self.intro = self.load_intro()


    def query(self, current_step=0,state=""):
        dialogs: List[Dialog] = []
        dialogs.append(
            [{"role": "user", "content": self.intro + state},
             ])

        results = self.generator.chat_completion(
            dialogs,  # type: ignore
            max_gen_len=self.max_gen_len,
            temperature=self.temperature,
            top_p=self.top_p,
        )
        output = results[0]['generation']['content']
        #print(output)
        #print("---- end of output of llama---")
        return output


class LLama2AgentWithCopy(Agent):
    def __init__(self, openended, num_agents, temperature, top_p, **kwargs):
        super().__init__(**kwargs)
        self.openended = openended
        self.num_agents = num_agents
        self.temperature = temperature
        self.top_p = top_p
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
        ckpt_dir = "/gpfsscratch/rech/imi/utw61ti/llama/llama-2-13b-chat"
        tokenizer_path = "/gpfsscratch/rech/imi/utw61ti/llama/tokenizer.model"
        self.max_seq_len =2200
        self.max_batch_size = 8
        #self.temperature = 1.0
        #self.top_p = 0.9
        self.max_gen_len =None
        self.generator = Llama.build(
            ckpt_dir=ckpt_dir,
            tokenizer_path=tokenizer_path,
            max_seq_len=self.max_seq_len,
            max_batch_size=self.max_batch_size,
            #model_parallel_size=8
        )
        self.intro = self.load_intro()


    def query(self, current_step=0,state=""):
        inventory = self.env.wordcraft_env.env.env.table

        # add inventory of others
        for agent in self.neighbors:
            inventory.extend(agent.env.wordcraft_env.env.table)
        inventory = list(set(inventory))
        self.env.wordcraft_env.env.env.table = inventory

        state = self.env.render()
        dialogs: List[Dialog] = []
        dialogs.append(
            [{"role": "user", "content": self.intro + state},
             ])

        results = self.generator.chat_completion(
            dialogs,  # type: ignore
            max_gen_len=self.max_gen_len,
            temperature=self.temperature,
            top_p=self.top_p,
        )
        output = results[0]['generation']['content']
        #print(output)
        #print("---- end of output of llama---")
        return output


class ChatgptAgent(Agent):


    def __init__(self, openended, num_agents,**kwargs):
        super().__init__(**kwargs)
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

        self.client = AzureOpenAI(
            azure_endpoint="https://eleni.openai.azure.com/",
            api_key=openai.api_key,
            api_version="2024-02-15-preview"
        )

        self.temperature = 1.0

        self.intro = self.load_intro()

    def query(self, current_step=0, state=""):
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
        return output


class ChatgptCulturalevoAgent(Agent):
    """" Chooses two random items from the inventory.
    """

    def __init__(self, openended, num_agents,**kwargs):
        super().__init__(**kwargs)
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

        if openai.api_key is None:
            print("You need to insert your API token to use chatgpt")
        self.temperature = 1.0

        self.intro = self.load_intro()

    def query(self, current_step=0, state=""):

        inventory = self.env.wordcraft_env.env.env.table

        # add inventory of others
        for agent in self.neighbors:
            inventory.extend(agent.env.wordcraft_env.env.table)
        inventory = list(set(inventory))
        self.env.wordcraft_env.env.env.table = inventory

        state = self.env.render()
        # quering openassistant
        messages = [{"role": "system", "content": "You are an intelligent and helpful assistant."}]

        messages.append({"role": "user", "content": self.intro})
        messages.append({"role": "user", "content": state})

        while True:
            try:

                chat = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=self.temperature,
                    top_p=1,
                )
                break

            except openai.error.APIError as e:
                # Handle API error here, e.g. retry or log
                print(f"OpenAI API returned an API Error: {e}")
                pass
            except openai.error.APIConnectionError as e:
                # Handle connection error here
                print(f"Failed to connect to OpenAI API: {e}")
                pass
            except openai.error.RateLimitError as e:
                # Handle rate limit error (we recommend using exponential backoff)
                print(f"OpenAI API request exceeded rate limit: {e}")
                pass

            except openai.error.ServiceUnavailableError as e:
                print(f"OpenAI API overloaded: {e}")
                pass
            except openai.error.Timeout as e:
                print(f"OpenAI API overloaded: {e}")
                pass

        output = chat.choices[0].message.content
        return output


class OAAgent(Agent):
    """" Chooses two random items from the inventory.
    """

    def __init__(self, openended, num_agents,**kwargs):
        super().__init__(**kwargs)
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
        memory = None

        temp = open(filename, 'r').readlines()
        intro = " ".join(temp)
        return intro
    def setup_llm(self):

        print("Loading openassistant-rlhf2-llama30b.")

        self.tokenizer = AutoTokenizer.from_pretrained(
            "/gpfswork/rech/imi/utw61ti/llama_data/oa_rlhf2/oasst-rlhf-2-llama-30b-7k-steps-xor/oasst-rlhf-2-llama"
            "-30b-7k-steps")
        print("tokenizer loaded")

        self.model = AutoModelForCausalLM.from_pretrained(
            "/gpfswork/rech/imi/utw61ti/llama_data/oa_rlhf2/oasst-rlhf-2-llama-30b-7k-steps-xor/oasst-rlhf-2-llama-30b-7k-steps")
        self.model.half().cuda()
        self.temperature = 1.0

        self.intro = self.load_intro()

    def query(self, current_step=0, state=""):
        # quering openassistant
        prompt = self.intro + state
        inputs = self.tokenizer(prompt, return_tensors='pt').to('cuda')
        output, _ = self.model.generate(
            **inputs,
            do_sample=True,
            temperature=self.temperature,
            top_k=20,
            max_new_tokens=90
        )
        output = self.tokenizer.batch_decode(output, skip_special_tokens=True)
        output = output[0][(len(prompt) - 3):]
        return output
