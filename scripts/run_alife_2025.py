import sys
import os
sys.path.append(os.getcwd())
from play import play, parse_flags



def run_single(agent_type):
    args = vars(parse_flags())
    args["results_dir"] = "results"
    args["num_steps"] = 200
    args["agent_type"] = agent_type
    args["openended"] = True
    args["num_tasks"] = 1
    args["num_agents"] = 1
    play(args)

if __name__ == "__main__":

    #run_llama3_group(connectivity="fully-connected")

    run_single(agent_type="ollama")
