import sys
import os
import argparse
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
    
    
def run_single_memory(agent_type, memory_type, num_steps=400,prob_artifact_disappear=0, memory_capacity=10):
    #agent_type = "ollama_memory"
    args = vars(parse_flags())
    args["num_trials"] = 2
    args["results_dir"] = "results"
    args["num_steps"] = num_steps
    args["agent_type"] = agent_type
    args["openended"] = True
    args["num_tasks"] = 1
    args["num_agents"] = 1
    args["memory_type"] = memory_type
    args["active_memory_capacity"] = memory_capacity
    args["prob_artifact_disappear"] = prob_artifact_disappear
    
    import time
    start_time = time.time()
    play(args)
    end_time = time.time()
    print(f"Run finished in {end_time - start_time:.2f} seconds.")
    
def run_all(agent_type):
    memory_types = ["random", "relevance", "recency"]
    memory_types = ["recency", "random"]
    prob_artifact_disappear_values = [0.0, 0.1]
    memory_capacity_values = [10, 50, 100]
    num_steps = 400
    
    for memory_type in memory_types:
        for prob_artifact_disappear in prob_artifact_disappear_values:
            for memory_capacity in memory_capacity_values:
                run_single_memory(agent_type,memory_type, num_steps, prob_artifact_disappear, memory_capacity)
                
                
def run_limited(agent_type):
    memory_types = ["random", "relevance", "recency"]
    memory_types = ["random"]
    prob_artifact_disappear_values = [0.0]
    memory_capacity_values = [10]
    num_steps = 400
    
    for memory_type in memory_types:
        for prob_artifact_disappear in prob_artifact_disappear_values:
            for memory_capacity in memory_capacity_values:
                run_single_memory(agent_type,memory_type, num_steps, prob_artifact_disappear, memory_capacity)
    
if __name__ == "__main__":
    run_all(agent_type="gemini")
    #run_limited(agent_type="gemini")










