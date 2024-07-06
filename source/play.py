""" This script the main interface to our code for running simulations.
It can be run directly by calling "python play.py --args" or by calling the method "play" from another script
"""

import os, sys
sys.path.append(os.getcwd())
import argparse
import pandas as pd
from datetime import datetime
import yaml
import time
import gym
from source.group import Group
from envs.wordcraft.wrappers.openended.wrapper import WordcraftEnv as open_env
from envs.wordcraft.wrappers.openended.recipe_book import Recipe as open_recipe
from envs.wordcraft.wrappers.targeted.wrapper import WordcraftEnv as target_env
from envs.wordcraft.wrappers.targeted.recipe_book import Recipe as target_recipe

# ----- general utils -----
def parse_flags():
    """ Parse flags that configure the experiment
     """
    parser = argparse.ArgumentParser()

    # ----- configure task ----
    parser.add_argument('--trial',
                        type=int,
                        default=0,
                        help='The index of the current trial. Trials with the same index contain the same tasks.')

    parser.add_argument('--num_tasks',
                        type=int,
                        default=20,
                        help='The number of tasks within each trial. Tasks differ in terms of available items and '
                             'target.')

    parser.add_argument('--num_steps',
                        type=int,
                        default=6,
                        help='Maximum number available to solve a single task.')

    parser.add_argument('--openended',
                        action='store_true',
                        help="If true, tasks do not have a target.")

    parser.add_argument('--encoded',
                        action='store_true',
                        help="If true, items in Wordcraft will be replaced by random symbols.")

    parser.add_argument('--num_distractors',
                        type=int,
                        default=6,
                        help='Only valid for targeted tasks, defines '
                             'The number of distractors (initial items not useful for crafting target)')

    parser.add_argument('--depth',
                        type=int,
                        default=1,
                        help='Only valid for targeted tasks, , defines the number of items needed to construct'
                             'the target item (in practise needs to be a small value because Wordcraft'
                             ' takes too long to discover tasks. ')

    # ----------------------------------------------------------------------------
    # ----- configure agent ----
    parser.add_argument('--agent_type',
                        type=str,
                        default="random",
                        help='The type of agent. Choose between openassistant, chatgpt, random, '
                             'uncertainty, empower and empower-onestep.')

    parser.add_argument('--forbid_repeats',
                        action='store_true',
                        help="If true, forbid baseline methods (we cannot directly forbid LLMs) from repeating an action within a task.")

    parser.add_argument('--retry',
                        type=int,
                        default=6,
                        help='Number of times an agent can re-attempt a step (due to choosing an already attempted action)')

    parser.add_argument('--temperature',
                        type=float,
                        help='Temperature for soft-max of LLM',
                        default=1)

    parser.add_argument('--top_p',
                        type=float,
                        help='Cut-off value for nucleus sampling of LLM',
                        default=0.9)

    # ----------------------------------------------------------------------------
    # ----- configure group ----

    parser.add_argument('--num_agents', type=int,
                        help='Number of agents',
                        default=1)

    parser.add_argument('--connectivity',
                        type=str,
                        help='Social connectivity. Choose between "fully-connected" and "dynamic"',
                        default="fully-connected")

    parser.add_argument('--visit_duration',
                        type=int,
                        help='Only valid for dynamic connectivity, defines the number of timesteps a visit lasts.',
                        default=5)

    parser.add_argument('--visit_prob',
                        type=float,
                        help='Only valid for dynamic connectivity, defines the probability that a random agent will visit'
                             'a random subgroup',
                        default=0.1)

    # ----------------------------------------------------------------------------

    args = parser.parse_args()
    return args


def setup_dir(args):
    """ Create a dedicated directory for the project.

    Params:
        args (dict): input flags configuring the project
    """
    top_dir = args["results_dir"]
    project_dir = [key + "_" + str(el) for key, el in args.items() if key != "trial" and key != "results_dir"]
    project_dir = top_dir + "results/" + datetime.today().strftime('%Y_%m_%d') + "/" + "_".join(project_dir) + "_70B"

    if not os.path.exists(project_dir + "/data"):
        os.makedirs(project_dir + "/data", exist_ok=True)

    with open(project_dir + "/config.yaml", "w") as f:
        yaml.dump(args, f, default_flow_style=False)

    print("Project created under directory: " + project_dir)

    return project_dir


def create_envs(env_args, seed):
    if env_args["openended"]:

        env = gym.make(
            'wordcraft-multistep-goal-v0',
            encoded=env_args["encoded"],
            max_mix_steps=env_args["steps"] + 1,
            seed=seed)
        env = open_env(env, encoded=env_args["encoded"])

    else:

        env = gym.make(
            'wordcraft-multistep-goal-v0',
            max_depth=env_args["depth"],
            max_mix_steps=env_args["steps"] + 1,
            num_distractors=env_args["distractors"],
            seed=seed)

        env = target_env(env, encoded=env_args["encoded"])

    env.reset()
    return env


def summarize_task(results, task):
    print("success for task " + str(task))
    print(results.loc[len(results) - 1]["success"])


def play(args):
    """ Main function for running a single trial.

    Params:
    args (dict): input flags configuring the project
    """
    # set up
    project_dir = setup_dir(args)

    env_args = {"openended": args["openended"],
                "steps": args["num_steps"],
                "encoded": args["encoded"],
                "depth": args["depth"],
                "distractors": args["num_distractors"]}

    # create group of agents
    group = Group(num_agents=args["num_agents"],
                  connectivity=args["connectivity"],
                  visit_prob=args["visit_prob"],
                  visit_duration=args["visit_duration"],
                  openended=args["openended"],
                  project_dir=project_dir,
                  trial=args["trial"],
                  model_name=args["model_name"],
                  forbid_repeats=args["forbid_repeats"],
                  temperature=args["temperature"],
                  top_p=args["top_p"])

    # will save experiment results here
    results = pd.DataFrame(columns=["trial",
                                    "task",
                                    "agent",
                                    "success",
                                    "steps",
                                    "count_repeated_valid",
                                    "count_repeated_invalid",
                                    "count_double_action",
                                    "count_repeated_valid_other",
                                    "count_repeated_invalid_other",
                                    "reward",
                                    "global_step",
                                    "action",
                                    "action_words",
                                    "invalid_attempts", "inventory_length", "copy_time",
                                    "perc_explore", "perc_explore_meaning"])

    start_time = time.time()
    for task in range(args["num_tasks"]):

        # creates a new environment for each agent
        envs = []
        for agent in group.agents:
            envs.append(create_envs(env_args, task))

        group.reset_task(task, envs)

        # step environment until the task is solved or maximum number of steps reached
        for step in range(args["num_steps"]):
            group_results = group.step(step)

            for agent_results in group_results:
                results.loc[len(results)] = agent_results

            if step % 50 == 0:
                # save all results
                with open(project_dir + "/data/results_" + str(args["trial"]) + ".pkl", "wb") as f:
                    results.to_pickle(f)

        group.wrap_up()

        with open(project_dir + "/data/results_" + str(args["trial"]) + ".pkl", "wb") as f:
            results.to_pickle(f)

        summarize_task(results, task)
    end_time = time.time()
    print("Trial ended. Results saved under " + project_dir + "/data/results_" + str(args["trial"]))
    print("Trial lasted: " + str(end_time-start_time) + " seconds.")


if __name__ == "__main__":
    args = vars(parse_flags())
    args["results_dir"] = "results"
    play(args)
