import os, sys
sys.path.append(os.getcwd())
from datetime import datetime
from structured_multi_LLM.play import play


def write_file( trial, temp, topp, connectivity, model):
    top_dir = "/gpfsscratch/rech/imi/utw61ti/multiLLM_log/"
    current_date = datetime.today().strftime('%Y_%m_%d')
    name = "/openended_temp_" + str(temp) + "_topp" + str(topp) + "_trial_" + str(trial) + "_conn_" + connectivity + "_model_" + model
    file_name = (top_dir + "jz_scripts/" + current_date  + "/multiagent/" + name + ".slurm")

    if not os.path.exists(top_dir + "jz_scripts/" + current_date + "/multiagent"):
        os.makedirs(top_dir + "jz_scripts/" + current_date + "/multiagent")
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
        command = "torchrun --nproc_per_node 2 scripts/reports/singleagent/server/openended_multi.py " + str(trial) + " " + str(temp) + " " + str(topp) + " " + str(connectivity) + " " + model
        file.write(command+ "\n")



if __name__ == "__main__":
    temp = 1.0
    topp = 0.9
    models = ["llama2", "llama2_copy"]
    for trial in range(10):
        for model in models:
            for connectivity in ["dynamic", "fully-connected"]:

                write_file(trial, temp, topp, connectivity, model)
