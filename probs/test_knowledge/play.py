import os, sys
sys.path.append(os.getcwd())
sys.path.append(os.getcwd()+"/wordcraft")
print(sys.path)
import numpy as np
import argparse
import pandas as pd
from datetime import datetime
import random
import yaml
import time
import gym
from probs.test_knowledge.group import Group
import pickle

# ----- general utils -----
def parse_flags():
    parser = argparse.ArgumentParser()

    parser.add_argument('--model_name',
                        type=str,
                        default="random",
                        help='The name of the language model. Choose between openassistant, chatgpt, random, '
                             'uncertainty, empower and empower-onestep.')

    parser.add_argument('--encoded',
                        action='store_true',
                        help="If true, words will be replaced by random symbols.")

    parser.add_argument('--forbid_repeats',
                        action='store_true',
                        help="If true, forbid baseline methods from repeating an action within a task.")

    parser.add_argument('--openended',
                        action='store_true',
                        help="If true, tasks do not have a target.")

    parser.add_argument('--trial',
                        type=int,
                        default=0,
                        help='The index of the current trial. All trials have the same tasks.')

    parser.add_argument('--num_tasks',
                        type=int,
                        default=20,
                        help='The number of tasks within each trial. Tasks differ in terms of available items and '
                             'target.')

    parser.add_argument('--num_distractors',
                        type=int,
                        default=6,
                        help='The number of distractors (initial items not useful for crafting target)')

    parser.add_argument('--depth',
                        type=int,
                        default=1,
                        help='Depth of tasks.')

    parser.add_argument('--num_steps',
                        type=int,
                        default=6,
                        help='Maximum number available to solve a single task.')

    parser.add_argument('--num_agents', type=int,
                        help='Number of agents',
                        default=1)

    parser.add_argument('--retry',
                        type=int,
                        default=6,
                        help='Number of times the llm can retry due to already tried combination')

    parser.add_argument('--temperature',
                        type=float,
                        help='temperature of llm',
                        default=1)

    parser.add_argument('--top_p',
                        type=float,
                        help='for llm sampling',
                        default=0.9)

    parser.add_argument('--connectivity',
                        type=str,
                        help='social network structure',
                        default="fully-connected")

    parser.add_argument('--visit_duration',
                        type=int,
                        help='social network structure',
                        default=5)

    parser.add_argument('--visit_prob',
                        type=float,
                        help='social network structure',
                        default=0.1)

    args = parser.parse_args()
    return args
def setup_dir(args):
    top_dir = args["results_dir"]
    project_dir = [key + "_" + str(el) for key, el in args.items() if key != "trial" and key != "results_dir"]
    project_dir = top_dir + "results/" + datetime.today().strftime('%Y_%m_%d') + "/knowledge_" + "_".join(project_dir)

    if not os.path.exists(project_dir + "/data"):
        os.makedirs(project_dir + "/data", exist_ok=True)

    with open(project_dir + "/config.yaml", "w") as f:
        yaml.dump(args, f, default_flow_style=False)

    print("project dir " + project_dir)

    return project_dir

def create_envs(env_args, seed):
    if env_args["openended"]:
        os.chdir("wordcraft")
        print(os.getcwd())
        from wordcraft_openended.env import WordCraftEnv

        env = gym.make(
            'wordcraft-multistep-goal-v0',
            encoded=env_args["encoded"],
            max_mix_steps=env_args["steps"] + 1,
            seed=seed)
        os.chdir("..")
        from envs.wordcraft.openended.wrapper import WordcraftEnvForLLM
        env = WordcraftEnvForLLM(env, encoded=env_args["encoded"])

    else:
        #os.chdir("wordcraft")
        #print(os.getcwd())

        from wordcraft.env import WordCraftEnv

        env = gym.make(
                'wordcraft-multistep-goal-v0',
                max_depth=env_args["depth"],
                max_mix_steps=env_args["steps"]+1,
                num_distractors=env_args["distractors"],
                seed=seed)
        #os.chdir("..")

        from envs.wordcraft.targeted.wrapper import WordcraftEnvForLLM
        env = WordcraftEnvForLLM(env, encoded=env_args["encoded"])


    env.reset()
    return env

def summarize_task(results, task):
    print("success for task " + str(task))
    print(results.loc[len(results)-1]["success"])

def play(args):
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
                                    "invalid_attempts", "inventory_length", "copy_time"])
    # load empowerment data
    with open("results/papers/openended/single/empower/data/results_" + str(args["trial"]) + ".pkl", "rb") as f:
        empower_results = pickle.load(f)
    empower_actions = empower_results[["action_words", "global_step"]]


    start_time = time.time()
    for task in range(args["num_tasks"]):

        # creates a new environment for each agent
        envs = []
        for agent in group.agents:
            envs.append(create_envs(env_args, task) )

        group.reset_task(task, envs)


        # step environment until the task is solved or maximum number of steps reached
        for step in range(args["num_steps"]):

            empower_actions_step = empower_actions.loc[empower_actions['global_step']==step]["action_words"].tolist()[0]
            group_results = group.step(step, empower_actions_step)

            # notice this has multilpe elements for each agent
            for agent_results in group_results:

                results.loc[len(results)] = agent_results
        group.wrap_up()

        summarize_task(results, task)

    # save al lresults
    with open(project_dir + "/data/results_" + str(args["trial"]) + ".pkl", "wb") as f:
        results.to_pickle(f)


    print("Trial ended. Results saved under " + project_dir + "/data/results_" + str(args["trial"]) )

if __name__ == "__main__":
    args = vars(parse_flags())
    args["results_dir"] = "results"
    play(args)


