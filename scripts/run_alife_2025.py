import sys
import os
sys.path.append(os.getcwd())
from play import play, parse_flags



def run_single(agent_type):
    args = vars(parse_flags())
    args["num_trials"] = 1
    args["results_dir"] = "results"
    args["num_steps"] = 200
    args["agent_type"] = agent_type
    args["openended"] = True
    args["num_tasks"] = 1
    args["num_agents"] = 1
    
    import time
    start_time = time.time()
    play(args)
    end_time = time.time()
    print(f"Run finished in {end_time - start_time:.2f} seconds.")
    
    
def run_single_memory(memory_type):
    agent_type="ollama_memory"
    args = vars(parse_flags())
    args["num_trials"] = 1
    args["results_dir"] = "results"
    args["num_steps"] = 200
    args["agent_type"] = agent_type
    args["openended"] = True
    args["num_tasks"] = 1
    args["num_agents"] = 1
    args["memory_type"] = "recency"
    
    import time
    start_time = time.time()
    play(args)
    end_time = time.time()
    print(f"Run finished in {end_time - start_time:.2f} seconds.")
    
if __name__ == "__main__":

    #run_single(agent_type="ollama")
    #run_single_memory(memory_type="recency")
    run_single_memory(memory_type="relevance")


