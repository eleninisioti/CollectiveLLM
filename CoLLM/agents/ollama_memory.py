""" An LLM player is provided with a prompt describing the task and the current state of the environment.
"""

import ollama
from CoLLM.agents.base import Agent

class OllamaAgentWithMemory(Agent):

    def __init__(self, seed, multiagent,  num_steps, forbid_repeats=False, memory_type="recency", **kwargs):
        self.forbid_repeats = forbid_repeats
        self.seed = seed
        self.memory_type = memory_type
        self.num_steps = num_steps
        # the form is item1, item2, output, timestep

        self.memory = []

        super().__init__(**kwargs)
        self.has_memory = True

        self.setup( multiagent)
        

    def setup(self, multiagent):
        if  multiagent:
            prompt_file = "la2/prompts/multitxt"
        else:
            prompt_file = "la2/prompts/single.txt"

        temp = open(prompt_file, 'r').readlines()
        self.intro = " ".join(temp)
        
    

    def parse_input(self, actions):
        def find_nth(haystack, needle, n):
            """ Find the nth occurrence of sub-string in string.
            """
            temp = haystack.find("Combination")
            start = haystack.find(needle)
            while start >= 0 and n > 1:
                start = haystack.find(needle, start + len(needle))
                n -= 1
            return start
    
        start_first = find_nth(actions, "Combination: '", 1)
        actions = actions[start_first:]
        start_first = find_nth(actions, "Combination: '", 1)
        end_first = find_nth(actions, "'", 2)
        first_word = actions[start_first + len("Combination: '"):end_first]
        end_second = find_nth(actions, "'", 4)
        second_word = actions[(end_first + 7): end_second]
        return first_word, second_word
    
    def rank_memory(self, memory, info):
        # relevance, recency, importance
        
        if self.memory_type == "recency":
            recency = memory[3]/self.num_steps
            print(recency, memory[3])
            rank = recency
        elif self.memory_type == "relevance":
          
            instructions = "You are currently playing a game. In this game I give you an inventory of items that you need to combine in pairs to make new items."
            instructions += "I will give you some information that has the form (item1, item2, output), where item1 and item2 can be combined to make output. "
            instructions += "If output is empty, this means that this combination is invalid, so it is not useful to you. "
            instructions += "Also if the output is already in your inventory, it is not useful to you, as you already have it. "
            instructions += "I want you to give me a value between 0 and 1 that characterizes how relevant this information is based on your current invenotry"
            instructions += "An information is relevant if it is likely to help you produce an item that you don't have or avoid attempting an item that is invalid or that you have already tried"
            
            
            content = instructions + "\n Here is the inventory: " + info + "\n Here is the information: " + memory  + "\n The relevance is: "
            response = ollama.chat(model='llama3.3', messages=[
                {
                    'role': 'user',
                    'content': content,
                },
            ])
            relevance = response['message']['content']
            rank = float(relevance)
        
        return rank
        
        
        
    def fetch_memory(self, info):
        # we check if the info is in the memory
        max_memories = 10
        
        if len(self.memory) > max_memories:
            ranks = []
            for memory in self.memory:
                
                rank = self.rank_memory(memory, info)
                ranks.append(rank)

            # Pair each memory with its rank
            memory_rank_pairs = list(zip(self.memory, ranks))
            # Sort by rank descending (assuming higher rank is better)
            memory_rank_pairs.sort(key=lambda x: x[1], reverse=True)
            # Take the top max_memories
            top_memories = memory_rank_pairs[:max_memories]
            # Extract just the memory part
            current_memory = [mem for mem, _ in top_memories]
        else:
            current_memory = self.memory
            
        
            
        memory_str = "Past valid combinations:\n"
        valid_combos = []
        invalid_combos = []

        for mem in current_memory:
            # Assuming mem is a tuple like (item1, item2, result)
            if  mem[2]:  # result exists and is not None/empty
                valid_combos.append(f"'{mem[0]}' and '{mem[1]}' -> '{mem[2]}'")
            else:
                invalid_combos.append(f"'{mem[0]}' and '{mem[1]}'")

        memory_str += "\n".join(valid_combos)
        memory_str += "\nPast invalid combinations:\n"
        memory_str += "\n".join(invalid_combos)

        return memory_str
    

    def _get_action(self):
        
        

        # Convert inventory (a list of strings) into a comma-separated string
        inventory_str = "\n Inventory: " + ", ".join(self.env.inventory)
        
        
        
        current_memory = self.fetch_memory(inventory_str)
        state = self.intro + inventory_str + current_memory

        print(current_memory)

        response = ollama.chat(model='llama3.3', messages=[
            {
                'role': 'user',
                'content': state,
            },
        ])
        response = response['message']['content']
        action = self.parse_input(response)
        
        print(response)
        if not len(action[0]) and not len(action[1]):
            self.invalid_actions += 1

        return action, response
