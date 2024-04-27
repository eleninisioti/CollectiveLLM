import os, sys

sys.path.append(os.getcwd())

from structured_multi_LLM.play import play
from datetime import datetime
import os


def write_file(model, num_agents, task_config, trial):
    top_dir = "/gpfsscratch/rech/imi/utw61ti/multiLLM_log/"
    current_date = datetime.today().strftime('%Y_%m_%d')
    name = "/model_" + model + "_numagents_" + str(num_agents) + "_depth_" + str(task_config[0]) + "_distr_" + str(task_config[1]) + "_trial_" + str(trial)

    file_name = (top_dir + "jz_scripts/" + current_date + name + ".slurm")

    if not os.path.exists(top_dir + "jz_scripts/" + current_date):
        os.makedirs(top_dir + "jz_scripts/" + current_date)
    # Open the file in write mode
    with open(file_name, "w") as file:

        file.write("#!/bin/bash"+ "\n")
        job_name = name
        file.write("#SBATCH --job-name=" + job_name + "\n")

        if model != "OA":
            file.write("#SBATCH -A imi@cpu" + "\n")
            file.write("#SBATCH --time=10:00:00" + "\n")
        else:

            file.write("#SBATCH -A imi@a100" + "\n")
            file.write("#SBATCH --gres=gpu:1 "+ "\n")
            file.write("#SBATCH -C a100"+ "\n")
            file.write("#SBATCH --cpus-per-task=60"+ "\n")
            file.write("#SBATCH --time=20:00:00"+ "\n")
        output_file = name  + "%j.out"
        file.write("#SBATCH --output=" + top_dir + "jz_logs" + output_file + "\n")
        error_file = name  + "%j.err"
        file.write("#SBATCH --error=" + top_dir + "jz_logs" + error_file+ "\n")
        file.write("source ~/.bashrc"+ "\n")
        file.write("conda activate openassistant"+ "\n")
        file.write("")
        command = "python structured_multi_LLM/play.py --model_name " + model + "  --trial " + str(trial) + " --num_tasks 20 --num_steps 6" + " --depth " + str(task_config[0])  + " --num_distractors " + str(task_config[1]) + " --num_agents " + str(num_agents)
        file.write(command+ "\n")

def write_file_openended(model, num_agents, connectivity,  trial):
    top_dir = "/gpfsscratch/rech/imi/utw61ti/multiLLM_log/"
    current_date = datetime.today().strftime('%Y_%m_%d')
    name = "/model_" + model + "_numagents_" + str(num_agents)  + "_trial_" + str(trial) + "_open"

    file_name = (top_dir + "jz_scripts/" + current_date + name + ".slurm")

    if not os.path.exists(top_dir + "jz_scripts/" + current_date):
        os.makedirs(top_dir + "jz_scripts/" + current_date)
    # Open the file in write mode
    with open(file_name, "w") as file:

        file.write("#!/bin/bash"+ "\n")
        job_name = name
        file.write("#SBATCH --job-name=" + job_name + "\n")

        if model != "OA":
            file.write("#SBATCH -A imi@cpu" + "\n")
            file.write("#SBATCH --time=10:00:00" + "\n")
        else:

            file.write("#SBATCH -A imi@a100" + "\n")
            file.write("#SBATCH --gres=gpu:1 "+ "\n")
            file.write("#SBATCH -C a100"+ "\n")
            file.write("#SBATCH --cpus-per-task=60"+ "\n")
            file.write("#SBATCH --time=20:00:00"+ "\n")
        output_file = name  + "%j.out"
        file.write("#SBATCH --output=" + top_dir + "jz_logs" + output_file + "\n")
        error_file = name  + "%j.err"
        file.write("#SBATCH --error=" + top_dir + "jz_logs" + error_file+ "\n")
        file.write("source ~/.bashrc"+ "\n")
        file.write("conda activate openassistant"+ "\n")
        file.write("")
        command = "python structured_multi_LLM/play.py --model_name " + model + "  --trial " + str(trial) + " --num_tasks 1 --openended --num_steps 100 --num_agents " + str(num_agents) + " --connectivity " + str(connectivity)
        file.write(command+ "\n")



def run_targeted():
    trials = 2
    group_sizes = [1, 3, 6]
    connectivity_types = ["fully-connected"]
    methods = ["OA"]
    task_configs = [[1,6], [2,3]]
    for task_config in task_configs:

        for num_agents in group_sizes:
            for trial in range(trials):
                write_file(num_agents=num_agents,
                           trial=trial,
                           task_config=task_config,
                           model="OA")


def run_openended():
    trials = 2
    group_sizes = [1, 6, 12]
    connectivity_types = ["dynamic", "fully-connected"]
    methods = ["OA"]

    for connectivity in connectivity_types:

        for num_agents in group_sizes:
            for trial in range(trials):
                write_file_openended(num_agents=num_agents,
                           trial=trial,
                                     connectivity=connectivity,
                           model="OA")


if __name__ == "__main__":

    #run_targeted(global_args)
    run_targeted()
    run_openended()


