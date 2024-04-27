import os, sys
sys.path.append(os.getcwd())

from structured_multi_LLM.play import play

config = {"retry": 6,
          "temperature": 1,
          "results_dir": "",
          "num_agents": 1,
          "visit_duration": None,
          "visit_prob": None,
          "connectivity": None,
          "encoded": False,
          "forbid_repeats": True,
          "top_p": 0.9}



def run_model(config):
    args = {**config}
    play(args)


def run_openended_baselines(num_trials):
    methods = ["random", "empower"]
    #methods = [ "llama2"]
    config["openended"] = True
    config["num_steps"] = 200
    config["num_distractors"] = None
    config["num_tasks"] = 1
    config["depth"] = None

    for method in methods:
        config["model_name"] = method

        for trial in range(num_trials):
            config["trial"] = trial

            play(config)


def run_targeted_baselines(num_trials):
    methods = ["random"]
    #methods = [ "llama2"]
    config["results_dir"] = ""
    config["openended"] = True
    config["encoded"] = True
    config["num_steps"] = 6
    config["num_distractors"] = 6
    config["num_tasks"] = 50
    config["depth"] =2

    for method in methods:
        config["model_name"] = method

        for trial in range(num_trials):
            config["trial"] = trial

            play(config)

def run_targeted_LLM(num_trials):
    #methods = ["random", "uncertainty", "empower"]
    methods = ["llama2"]
    config["results_dir"] = "/gpfsscratch/rech/imi/utw61ti/multiLLM/"
    config["openended"] = False
    config["num_steps"] = 6
    config["num_distractors"] = 3
    config["num_tasks"] = 50
    config["depth"] = 1

    for method in methods:
        config["model_name"] = method

        for trial in range(num_trials):
            config["trial"] = trial

            play(config)

if __name__ == "__main__":
    #run_targeted_baselines(num_trials=10)
    #run_openended_baselines(num_trials=10)

    #run_openended_baselines(num_trials=10)
    #run_targeted_LLM(num_trials=2)