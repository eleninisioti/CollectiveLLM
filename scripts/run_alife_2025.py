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
    
    
def run_single_memory(memory_type, num_steps=400,prob_artifact_disappear=0, memory_capacity=10):
    agent_type = "ollama_memory"
    args = vars(parse_flags())
    args["num_trials"] = 1
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
    
if __name__ == "__main__":
    #run_single_memory(memory_type="relevance", prob_artifact_disappear=0, memory_capacity=10)
    #run_single_memory(memory_type="random", prob_artifact_disappear=0.1, memory_capacity=100, num_steps=400)
    run_single_memory(  memory_type="random", prob_artifact_disappear=0.0, memory_capacity=100, num_steps=100)
    run_single_memory(memory_type="random", prob_artifact_disappear=0.0, memory_capacity=10, num_steps=100)

    #run_single_memory(memory_type="recency", prob_artifact_disappear=0.0, memory_capacity=50, num_steps=400)
    #run_single_memory(memory_type="relevance", prob_artifact_disappear=0.1, memory_capacity=10)









