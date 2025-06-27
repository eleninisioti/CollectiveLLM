import sys
import os
import argparse
sys.path.append(os.getcwd())
from play import play, parse_flags
import time



def run_random(agent_type):
    args = vars(parse_flags())
    args["num_trials"] = 1
    args["results_dir"] = "results"
    args["num_steps"] = 500
    args["agent_type"] = agent_type
    args["openended"] = True
    args["num_tasks"] = 1
    args["num_agents"] = 6
    args["memory_type"] = None
    connectivies = ["dynamic", "fully-connected"]
    
    for connectivity in connectivies:
        args["connectivity"] = connectivity
        start_time = time.time()
        play(args)
        end_time = time.time()
        print(f"Run finished in {end_time - start_time:.2f} seconds.")
    

    

                

    
if __name__ == "__main__":
    run_random(agent_type="random")
    










