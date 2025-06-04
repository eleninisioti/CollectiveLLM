import yaml
import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


fig_size = (8.27/2, 11.69/4)  # A4 column width in inches (portrait orientation)

plt.rcParams["figure.figsize"] = fig_size
plt.rcParams.update({'font.size': 11})


def viz_metrics(project_dir):
    save_dir = project_dir + "/visuals"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    with open(project_dir + "/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    n_trials = config["num_trials"]

    data = []
    for trial in range(n_trials):
        with open(project_dir + "/data/results_" + str(trial) + ".pkl", "rb") as f:
            data.append(pickle.load(f))
            
    # Take all columns of data except 'steps'
            
    data = pd.concat(data, ignore_index=True)
    print(data)
    metrics = [col for col in data.columns if col != 'steps']

    
        

    for metric in metrics:
        # ----- plot average across tasks and population -----
        plt.figure()
        sns.lineplot(
            x='steps',
            y= metric,
            data=data,
            ci='sd')
        #    plt.xlabel('Task')
        plt.ylabel(metric)
        plt.savefig(save_dir + "/" + metric + ".png")
        plt.clf()

def viz_project(project_dir):

    viz_metrics(project_dir)
    
    
if __name__ == "__main__":
    project_dir = "results/2025_06_02/num_trials_1_num_tasks_1_num_steps_200_openended_True_encoded_False_num_distractors_6_depth_1_agent_type_ollama_forbid_repeats_False_retry_6_temperature_1_top_p_0.9_num_agents_1_connectivity_fully-connected_visit_duration_5_visit_prob_0.1_70B"
    viz_project(project_dir)
