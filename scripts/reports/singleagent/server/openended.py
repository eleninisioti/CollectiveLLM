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
          "forbid_repeats": True}

def run_openended_LLM(trial, temp, topp):
    config["results_dir"] = "/gpfsscratch/rech/imi/utw61ti/multiLLM/"
    config["openended"] = True
    config["num_steps"] = 500
    config["num_distractors"] = 1
    config["num_tasks"] = 1
    config["depth"] = 1
    config["model_name"] = "llama2"
    config["temperature"] = temp
    config["top_p"] = topp
    config["trial"] = trial

    play(config)

if __name__ == "__main__":
    trial = int(sys.argv[1])
    temp = float(sys.argv[2])
    topp = float(sys.argv[3])

    run_openended_LLM(trial, temp, topp)