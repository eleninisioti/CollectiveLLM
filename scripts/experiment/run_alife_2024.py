import sys
import os
sys.path.append(os.getcwd())
from play import play, parse_flags

def run_llama3_group(connectivity):

    args = vars(parse_flags())
    args["results_dir"] = "results"
    args["num_steps"] = 300
    args["num_trials"] = 1
    args["agent_type"] = "llama3"
    args["connectivity"] = connectivity
    args["openended"] = True
    args["num_tasks"] = 1
    args["num_agents"] = 6
    play(args)

def run_llama3():
    args = vars(parse_flags())
    args["results_dir"] = "results"
    args["num_steps"] = 200
    args["agent_type"] = "llama3"
    args["openended"] = True
    args["num_tasks"] = 1
    args["num_agents"] = 1
    play(args)

if __name__ == "__main__":

    #run_llama3_group(connectivity="fully-connected")

    run_llama3_group(connectivity="dynamic")


    #run_llama3()

