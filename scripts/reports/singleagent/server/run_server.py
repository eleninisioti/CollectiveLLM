import os, sys
sys.path.append(os.getcwd())
from datetime import datetime


def write_file( num_distractors, num_levels, trial):
    top_dir = "/gpfsscratch/rech/imi/utw61ti/multiLLM_log/"
    current_date = datetime.today().strftime('%Y_%m_%d')
    name = "/distractors_"+ str(num_distractors) + "_levels_" + str(num_levels) + "_trial_" + str(trial)
    file_name = (top_dir + "jz_scripts/" + current_date + name + ".slurm")

    if not os.path.exists(top_dir + "jz_scripts/" + current_date):
        os.makedirs(top_dir + "jz_scripts/" + current_date)
    # Open the file in write mode
    with open(file_name, "w") as file:

        file.write("#!/bin/bash"+ "\n")
        job_name = name
        file.write("#SBATCH --job-name=" + job_name + "\n")


        file.write("#SBATCH -A imi@v100" + "\n")
        file.write("#SBATCH --gres=gpu:2 "+ "\n")
        file.write("#SBATCH --cpus-per-task=13"+ "\n")
        file.write("#SBATCH --time=05:00:00"+ "\n")
        file.write("#SBATCH --hint=nomultithread" + "\n")
        file.write("#SBATCH --partition=gpu_p2l" + "\n")
        output_file = name  + "%j.out"
        file.write("#SBATCH --output=" + top_dir + "jz_logs" + output_file + "\n")
        error_file = name  + "%j.err"
        file.write("#SBATCH --error=" + top_dir + "jz_logs" + error_file+ "\n")
        file.write("source ~/.bashrc"+ "\n")
        file.write("conda activate llm"+ "\n")
        file.write("")
        command = "torchrun --nproc_per_node 2 scripts/reports/singleagent/server/targeted.py " + str(num_distractors) + " " + str(num_levels) + " " + str(trial)
        file.write(command+ "\n")


def parametric():
    for trial in range(1,10):

        for num_distractors in [3,6]:
            for num_levels in [1,2]:
                write_file(num_distractors, num_levels, trial)

def semantics():
    num_distractors = 3
    num_levels = 1
    for trial in range(1,10):

        write_file(num_distractors, num_levels, trial)

if __name__ == "__main__":
    semantics()


