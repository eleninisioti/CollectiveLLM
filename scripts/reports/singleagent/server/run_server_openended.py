import os, sys
sys.path.append(os.getcwd())
from datetime import datetime
from structured_multi_LLM.play import play


def write_file( trial, temp, topp):
    top_dir = "/gpfsscratch/rech/imi/utw61ti/multiLLM_log/"
    current_date = datetime.today().strftime('%Y_%m_%d')
    name = "/openended_temp_" + str(temp) + "_topp" + str(topp) + "_trial_" + str(trial)
    file_name = (top_dir + "jz_scripts/" + current_date + name + ".slurm")

    if not os.path.exists(top_dir + "jz_scripts/" + current_date):
        os.makedirs(top_dir + "jz_scripts/" + current_date)
    # Open the file in write mode
    with open(file_name, "w") as file:

        file.write("#!/bin/bash"+ "\n")
        job_name = name
        file.write("#SBATCH --job-name=" + job_name + "\n")


        file.write("#SBATCH -A imi@v100" + "\n")
        file.write("#SBATCH --gres=gpu:1 "+ "\n")
        file.write("#SBATCH --cpus-per-task=16"+ "\n")
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
        command = "torchrun --nproc_per_node 1 scripts/reports/singleagent/server/openended.py " + str(trial) + " " + str(temp) + " " + str(topp)
        file.write(command+ "\n")



if __name__ == "__main__":

    temp = 0.7
    topp = 0.98
    for trial in range(1, 5):
        write_file(trial, temp, topp)

        #for temp in [1.0, 1.5, 2.0]:
            #for topp in [0.5, 0.8, 0.9]:
