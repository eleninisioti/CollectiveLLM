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
          "top_p": 0.9,
          "encoded": False,
          "forbid_repeats": True}

def run_targeted_LLM(num_distractors, num_levels, trial):
    config["results_dir"] = "/gpfsscratch/rech/imi/utw61ti/multiLLM/"
    config["openended"] = False
    config["num_steps"] = 6
    config["num_distractors"] = num_distractors
    config["num_tasks"] = 50
    config["depth"] = num_levels
    config["model_name"] = "llama2"

    config["trial"] = trial

    play(config)

def run_without_semantics(num_distractors, num_levels, trial):
    config["results_dir"] = "/gpfsscratch/rech/imi/utw61ti/multiLLM/"
    config["openended"] = False
    config["encoded"] = True
    config["num_steps"] = 6
    config["num_distractors"] = num_distractors
    config["num_tasks"] = 50
    config["depth"] = num_levels
    config["model_name"] = "llama2"

    config["trial"] = trial

    play(config)

if __name__ == "__main__":
    num_distractors = int(sys.argv[1])
    num_levels = int(sys.argv[2])
    trial = int(sys.argv[3])
    #run_targeted_LLM(num_distractors, num_levels, trial)
    run_without_semantics(num_distractors, num_levels, trial)