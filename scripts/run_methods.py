import os, sys

sys.path.append(os.getcwd())

from structured_multi_LLM.play import play

def run_model(global_args, depth, num_steps, distractors, trial, num_tasks, openended, num_agents, connectivity, model_name, forbid_repeats):
    args = {**global_args, **{"depth": depth,
                          "num_distractors": distractors,
                          "trial": trial,
                          "model_name": "random",
                          "encoded": False,
                          "openended": openended,
                          "num_tasks": num_tasks,
                          "num_agents": num_agents,
                          "connectivity": connectivity,
                          "model_name": model_name,
                              "num_steps": num_steps,
                              "forbid_repeats": forbid_repeats}}
    play(args)



def run_targeted(global_args):
    num_tasks = 20
    trials = 2
    group_sizes = [1]
    connectivity_types = ["fully-connected"]
    methods = ["random"]
    for model_name in methods:

        for connectivity in connectivity_types:
            for num_agents in group_sizes:
                for trial in range(trials):
                    run_model(global_args=global_args,
                               trial=trial,
                               num_tasks=num_tasks,
                               depth=1,
                               distractors=6,
                               openended=False,
                               num_agents=num_agents,
                               connectivity=connectivity,
                              model_name=model_name)

def run_debug(global_args):
    num_trials = 2
    for trial in range(num_trials):
        # run random, 1 agent, 6 distractors, targeted
        #run_model(global_args=global_args, steps=6, trial=trial, num_tasks=20,depth=1,distractors=6,wordcraft_openended=False,num_agents=1,connectivity="fully_connected", model_name="random")

        # run uncertainty, 1 agent, 6 distractors, targeted
        #run_model(global_args=global_args, steps=6, trial=trial, num_tasks=20, depth=1, distractors=6, wordcraft_openended=False,
        #          num_agents=1, connectivity="fully_connected", model_name="uncertainty")
        #run_model(global_args=global_args, steps=6, trial=trial, num_tasks=20, depth=1, distractors=6, wordcraft_openended=False,
        #          num_agents=1, connectivity="fully_connected", model_name="empower")
        #run_model(global_args=global_args, steps=6, trial=trial, num_tasks=20, depth=1, distractors=6, wordcraft_openended=False,
        #          num_agents=1, connectivity="fully_connected", model_name="empower_onestep")

        run_model(global_args=global_args, num_steps=6, trial=trial, num_tasks=20, depth=1, distractors=6, openended=False,
                  num_agents=1, connectivity="fully_connected", model_name="chatgpt")

def run_2level(global_args, forbid_repeats):

    num_trials = 10
    num_tasks = 10
    for trial in range(num_trials):
        # run random, 1 agent, 6 distractors, targeted
        run_model(global_args=global_args, num_steps=6, trial=trial, num_tasks=num_tasks,depth=2,distractors=3,openended=False,num_agents=1,connectivity="fully_connected", model_name="random", forbid_repeats=forbid_repeats)

        # run uncertainty, 1 agent, 6 distractors, targeted
        run_model(global_args=global_args, num_steps=6, trial=trial, num_tasks=num_tasks, depth=2, distractors=3, openended=False,
                  num_agents=1, connectivity="fully_connected", model_name="uncertainty", forbid_repeats=forbid_repeats)
        run_model(global_args=global_args, num_steps=6, trial=trial, num_tasks=num_tasks, depth=2, distractors=3, openended=False,
                  num_agents=1, connectivity="fully_connected", model_name="empower", forbid_repeats=forbid_repeats)
        run_model(global_args=global_args, num_steps=6, trial=trial, num_tasks=num_tasks, depth=2, distractors=3, openended=False,
                  num_agents=1, connectivity="fully_connected", model_name="empower_onestep", forbid_repeats=forbid_repeats)

def run_1level(global_args, forbid_repeats):

    num_trials = 10
    num_tasks = 10
    for trial in range(num_trials):
        # run random, 1 agent, 6 distractors, targeted
        run_model(global_args=global_args, num_steps=6, trial=trial, num_tasks=num_tasks,depth=1,distractors=6,openended=False,num_agents=6,connectivity="fully-connected", model_name="random", forbid_repeats=forbid_repeats)

        # run uncertainty, 1 agent, 6 distractors, targeted
        run_model(global_args=global_args, num_steps=6, trial=trial, num_tasks=num_tasks, depth=1, distractors=6, openended=False,
                  num_agents=1, connectivity="fully_connected", model_name="uncertainty", forbid_repeats=forbid_repeats)
        run_model(global_args=global_args, num_steps=6, trial=trial, num_tasks=num_tasks, depth=1, distractors=6, openended=False,
                  num_agents=1, connectivity="fully_connected", model_name="empower", forbid_repeats=forbid_repeats)
        run_model(global_args=global_args, num_steps=6, trial=trial, num_tasks=num_tasks, depth=1, distractors=6, openended=False,
                  num_agents=1, connectivity="fully_connected", model_name="empower_onestep", forbid_repeats=forbid_repeats)


def run_1level_chatgpt(global_args, forbid_repeats):

    num_trials = 2
    num_tasks = 10
    for trial in range(num_trials):
        #  1 agent
        #run_model(global_args=global_args, num_steps=6, trial=trial, num_tasks=num_tasks,depth=1,distractors=6,openended=False,num_agents=1,connectivity="fully-connected", model_name="chatgpt", forbid_repeats=forbid_repeats)

        # 3 agents
        run_model(global_args=global_args, num_steps=6, trial=trial, num_tasks=num_tasks,depth=1,distractors=6,openended=False,num_agents=3,connectivity="fully-connected", model_name="chatgpt", forbid_repeats=forbid_repeats)


def run_2level_chatgpt(global_args, forbid_repeats):

    num_trials = 1
    num_tasks = 10
    for trial in range(num_trials):
        #  1 agent
        #run_model(global_args=global_args, num_steps=6, trial=trial, num_tasks=num_tasks,depth=2,distractors=3,openended=False,num_agents=1,connectivity="fully-connected", model_name="chatgpt", forbid_repeats=forbid_repeats)

        # 3 agents
        run_model(global_args=global_args, num_steps=6, trial=trial, num_tasks=num_tasks,depth=2,distractors=3,openended=False,num_agents=2,connectivity="fully-connected", model_name="chatgpt", forbid_repeats=forbid_repeats)
def run_openended_chatgpt(global_args, forbid_repeats):

    num_trials = 1
    num_tasks = 1
    for trial in range(num_trials):
        #  1 agent
        #run_model(global_args=global_args, num_steps=100, trial=trial, num_tasks=num_tasks,depth=2,distractors=3,openended=True,num_agents=1,connectivity="fully-connected", model_name="chatgpt", forbid_repeats=forbid_repeats)

        # 3 agents
        run_model(global_args=global_args, num_steps=100, trial=trial, num_tasks=num_tasks,depth=2,distractors=3,openended=True,num_agents=6,connectivity="dynamic", model_name="chatgpt", forbid_repeats=forbid_repeats)

def run_openended_culturalevo(global_args, forbid_repeats):
    # run baseline methods, with and withourt repeats

    num_trials = 1
    num_steps= 200


    for trial in range(num_trials):
        # run random, 1 agent, 6 distractors, targeted
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1,depth=1,distractors=6, num_agents=6,connectivity="fully-connected", model_name="random", forbid_repeats=forbid_repeats, openended=True)
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1,depth=1,distractors=6, num_agents=6,connectivity="dynamic", model_name="random", forbid_repeats=forbid_repeats, openended=True)


        """
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1,depth=1,distractors=6, num_agents=6,connectivity="fully-connected", model_name="random", forbid_repeats=forbid_repeats, openended=True)

        # run uncertainty, 1 agent, 6 distractors, targeted
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
                  num_agents=1, connectivity="fully_connected", model_name="uncertainty", forbid_repeats=forbid_repeats, openended=True)
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
                  num_agents=1, connectivity="fully_connected", model_name="empower", forbid_repeats=forbid_repeats, openended=True)
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
                  num_agents=1, connectivity="fully_connected", model_name="empower_onestep", forbid_repeats=forbid_repeats, openended=True)
        """
    # run chatgpt with repeats
    """
    num_trials = 1
    for trial in range(num_trials):
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
                  openended=True,
                  num_agents=1, connectivity="fully_connected", model_name="chatgpt",forbid_repeats=forbid_repeats)
    """


def run_openended_chatgpt_forculturalevo(global_args, forbid_repeats):
    # run baseline methods, with and withourt repeats

    num_trials = 1
    num_steps= 200


    for trial in range(num_trials):
        # run random, 1 agent, 6 distractors, targeted
        #
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1,depth=1,distractors=6, num_agents=6,connectivity="dynamic", model_name="chatgpt", forbid_repeats=forbid_repeats, openended=True)
        #run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1,depth=1,distractors=6, num_agents=6,connectivity="dynamic", model_name="chatgpt", forbid_repeats=forbid_repeats, openended=True)

        #run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1,depth=1,distractors=6, num_agents=6,connectivity="dynamic", model_name="cultural_evo", forbid_repeats=forbid_repeats, openended=True)


        """
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1,depth=1,distractors=6, num_agents=6,connectivity="fully-connected", model_name="random", forbid_repeats=forbid_repeats, openended=True)

        # run uncertainty, 1 agent, 6 distractors, targeted
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
                  num_agents=1, connectivity="fully_connected", model_name="uncertainty", forbid_repeats=forbid_repeats, openended=True)
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
                  num_agents=1, connectivity="fully_connected", model_name="empower", forbid_repeats=forbid_repeats, openended=True)
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
                  num_agents=1, connectivity="fully_connected", model_name="empower_onestep", forbid_repeats=forbid_repeats, openended=True)
        """
    # run chatgpt with repeats
    """
    num_trials = 1
    for trial in range(num_trials):
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
                  openended=True,
                  num_agents=1, connectivity="fully_connected", model_name="chatgpt",forbid_repeats=forbid_repeats)
    """


def run_openended_empower(global_args, forbid_repeats):
    # run baseline methods, with and withourt repeats

    num_trials = 1
    num_steps= 200


    for trial in range(num_trials):
        # run random, 1 agent, 6 distractors, targeted
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1,depth=1,distractors=6, num_agents=1,connectivity="fully-connected", model_name="noisyv2_empower", forbid_repeats=forbid_repeats, openended=True)
        """
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1,depth=1,distractors=6, num_agents=6,connectivity="fully-connected", model_name="random", forbid_repeats=forbid_repeats, openended=True)

        # run uncertainty, 1 agent, 6 distractors, targeted
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
                  num_agents=1, connectivity="fully_connected", model_name="uncertainty", forbid_repeats=forbid_repeats, openended=True)
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
                  num_agents=1, connectivity="fully_connected", model_name="empower", forbid_repeats=forbid_repeats, openended=True)
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
                  num_agents=1, connectivity="fully_connected", model_name="empower_onestep", forbid_repeats=forbid_repeats, openended=True)
        """
    # run chatgpt with repeats
    """
    num_trials = 1
    for trial in range(num_trials):
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
                  openended=True,
                  num_agents=1, connectivity="fully_connected", model_name="chatgpt",forbid_repeats=forbid_repeats)
    """

def run_openendedmulti(global_args, num_agents, connectivity, forbid_repeats):
    # run baseline methods, with and withourt repeats
    num_trials = 3
    num_steps=100

    for trial in range(num_trials):
        # run random, 1 agent, 6 distractors, targeted
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1,depth=1,distractors=6, num_agents=num_agents,connectivity=connectivity, model_name="random", forbid_repeats=forbid_repeats, openended=True)

        # run uncertainty, 1 agent, 6 distractors, targeted
        #run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
        #          num_agents=num_agents, connectivity=connectivity, model_name="uncertainty", forbid_repeats=forbid_repeats, openended=True)
        #run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
        #          num_agents=num_agents, connectivity=connectivity, model_name="empower", forbid_repeats=forbid_repeats, openended=True)
        #run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
        #          num_agents=num_agents, connectivity=connectivity, model_name="empower_onestep", forbid_repeats=forbid_repeats, openended=True)
    # run chatgpt with repeats
    """
    num_trials = 1
    for trial in range(num_trials):
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
                  wordcraft_openended=False,
                  num_agents=1, connectivity="fully_connected", model_name="chatgpt")
    """


def run_chatgpt(global_args):

    # run openended with multiple agents and fully-connected
    num_trials = 1
    num_steps = 100
    connectivity = "dynamic"
    num_agents=1
    forbid_repeats = True

    for trial in range(num_trials):
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
                  num_agents=num_agents, connectivity=connectivity, model_name="chatgpt", forbid_repeats=forbid_repeats,
                  openended=True)

    # then run dynamic

def run_chatgpt_targeted(global_args):

    # run openended with multiple agents and fully-connected
    num_trials = 1
    num_steps = 6
    connectivity = "fully-connected"
    num_agents= 3
    forbid_repeats = True

    for trial in range(num_trials):
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=10, depth=1, distractors=6,
                  num_agents=num_agents, connectivity=connectivity, model_name="chatgpt", forbid_repeats=forbid_repeats,
                  openended=False)

        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=10, depth=2, distractors=3,
                  num_agents=num_agents, connectivity=connectivity, model_name="chatgpt", forbid_repeats=forbid_repeats,
                  openended=False)

    # then run dynamic

def run_chatgpt_empower(global_args):

    # run openended with multiple agents and fully-connected
    num_trials = 1
    num_steps = 100
    connectivity = "dynamic"
    num_agents=1
    forbid_repeats = True

    for trial in range(num_trials):
        run_model(global_args=global_args, num_steps=num_steps, trial=trial, num_tasks=1, depth=1, distractors=6,
                  num_agents=num_agents, connectivity=connectivity, model_name="chatgpt", forbid_repeats=forbid_repeats,
                  openended=True)

    # then run dynamic

if __name__ == "__main__":
    global_args = {"retry": 6,
                   "temperature": 1,
                   "visit_duration": 50,
                   "visit_prob": 0.2,
                   "results_dir": ""}



    #run_1level(global_args, forbid_repeats=True)
    #run_2level(global_args, forbid_repeats=True)
    #run_1level_chatgpt(global_args, forbid_repeats=True)
    #run_2level_chatgpt(global_args, forbid_repeats=True)
    #run_openended_chatgpt(global_args, forbid_repeats=True)
    #run_openended_empower(global_args, forbid_repeats=True)
    #run_openended_culturalevo(global_args, forbid_repeats=True)
    run_openended_chatgpt_forculturalevo(global_args, forbid_repeats=True)




    """
    run_2level(global_args, forbid_repeats=False)
    """
    #run_openended(global_args, forbid_repeats=True)

    #run_openended(global_args, forbid_repeats=False)
    #run_openendedmulti(global_args, num_agents=6, forbid_repeats=True, connectivity="fully-connected")


    #run_openendedmulti(global_args, num_agents=6, forbid_repeats=True, connectivity="dynamic")
    #run_chatgpt_targeted(global_args)
    #run_chatgpt_empower(global_args)

    # now tridy up and ready to run multiagent chatgpt and then you are done :D
    #run_openendedmulti(global_args,num_agents=6,connectivity="dynamic")

