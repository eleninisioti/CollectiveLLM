import sys
import os
import argparse
import wandb
sys.path.append(os.getcwd())
from play import play, parse_flags
import time



def run(agent_type):
    args = vars(parse_flags())
    args["num_trials"] = 10
    args["results_dir"] = "results"
    args["num_steps"] = 200
    args["agent_type"] = agent_type
    args["openended"] = True
    args["num_tasks"] = 1
    args["num_agents"] = 10
    args["memory_type"] = None
    args["prob_visit"] = 0.01
    args["visit_duration"] = 5
    connectivities = ["dynamic", "fully-connected"]
    connectivities = ["dynamic"]
    #connectivities = ["fully-connected"]
    wandb.init(project="collective-llm-single")
    
    for connectivity in connectivities:
        args["connectivity"] = connectivity
        start_time = time.time()
        play(args)
        end_time = time.time()
        print(f"Run finished in {end_time - start_time:.2f} seconds.")
    

def run_wandb_sweep():
    """Run a wandb sweep for the experiment."""
    # Initialize wandb
    wandb.init(project="collective-llm-sweep")
    
    # Get parameters from wandb config
    config = wandb.config
    
    # Set up arguments
    args = vars(parse_flags())
    args["num_trials"] = 1
    args["results_dir"] = "results"
    args["num_steps"] = 500
    args["agent_type"] = "random"
    args["openended"] = True
    args["num_tasks"] = 1
    args["memory_type"] = None
    args["connectivity"] = "dynamic"
    
    # Update with sweep parameters
    args["prob_visit"] = config.prob_visit
    args["visit_duration"] = config.visit_duration
    args["num_agents"] = config.num_agents
    
    print(f"Running with: prob_visit={config.prob_visit}, visit_duration={config.visit_duration}, num_agents={config.num_agents}")
    
    start_time = time.time()
    play(args)
    end_time = time.time()
    
    # Log metrics to wandb
    wandb.log({
        "runtime": end_time - start_time,
        "prob_visit": config.prob_visit,
        "visit_duration": config.visit_duration,
        "num_agents": config.num_agents
    })
    
    print(f"Run finished in {end_time - start_time:.2f} seconds.")

def create_sweep_config():
    """Create the wandb sweep configuration."""
    sweep_config = {
        "method": "grid",  # or "random", "bayes"
        "name": "collective-llm-parameter-sweep-random",
        "metric": {
            "name": "mean_inventory_size",
            "goal": "maximize"
        },
        "parameters": {
            "prob_visit": {
                "values": [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5]
            },
            "visit_duration": {
                "values": [2, 5, 10, 20, 50]
            },
            "num_agents": {
                "values": [10]
            }
        }
    }
    return sweep_config

if __name__ == "__main__":
    # Choose which method to run
    run_type = "wandb_sweep"  # Change to "single" for the original run method
    run_type = "single"
    if run_type == "wandb_sweep":
        # Create and run the sweep
        sweep_config = create_sweep_config()
        sweep_id = wandb.sweep(sweep_config, project="collective-llm-sweep")
        wandb.agent(sweep_id, function=run_wandb_sweep)  # 7*5*3 = 105 total runs
    else:
        run(agent_type="empower")
    










