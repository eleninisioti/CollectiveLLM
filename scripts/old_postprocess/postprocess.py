import yaml
import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob


fig_size = (8.27/2*2, 11.69/4*2)  # A4 column width in inches (portrait orientation)

plt.rcParams["figure.figsize"] = fig_size
plt.rcParams.update({'font.size': 11})


def get_label(dir_name):
    # Extract memory type and number from directory name
    if 'mem_random_act_100' in dir_name:
        return 'random_100'
    elif 'mem_random_act_10' in dir_name:
        return 'random_10'
    elif 'mem_recency_act_10' in dir_name:
        return 'recency_10'
    elif 'mem_relevance_act_10' in dir_name:
        return 'relevance_10'
    return dir_name[-25:]  # fallback to last 25 chars if no match

def viz_metrics(project_dir, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    with open(project_dir + "/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    n_trials = config["num_trials"]

    data = []
    for trial in range(n_trials):
        with open(project_dir + "/data/results_" + str(trial) + ".pkl", "rb") as f:
            #temp = pickle.load(f)
            data.append(pickle.load(f))
            
    data = pd.concat(data, ignore_index=True)
    metrics = [col for col in data.columns if col != 'steps']
    #metrics.remove("items")
    
    # Add directory name as a column for grouping
    dir_name = os.path.basename(project_dir)
    # Map directory name to specific label
    data['directory'] = get_label(dir_name)
    
    return data, metrics

def viz_project(base_dir):
    # Create visuals directory
    visuals_dir = os.path.join(base_dir, "visuals")

    if not os.path.exists(visuals_dir):
        os.makedirs(visuals_dir)
    
    # Get all subdirectories
    subdirs = [d for d in glob.glob(os.path.join(base_dir, "*")) if os.path.isdir(d) and "visuals" not in d]
    
    # Collect data from all directories
    all_data = []
    all_metrics = set()
    
    for subdir in subdirs:
        
        config_file = os.path.join(subdir, "config.yaml")
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        agent_type = config["agent_type"]

        data, metrics = viz_metrics(subdir, os.path.join(subdir, "visuals"))
        
        
        all_data.append(data)
        all_metrics.update(metrics)

    
    if not all_data:
        print("No valid data found in any directory")
        return
        
    # Combine all data
    combined_data = pd.concat(all_data, ignore_index=True)
    
    # Create consolidated plots for each metric
    for metric in all_metrics:
        plt.figure()
        sns.lineplot(
            x='steps',
            y=metric,
            hue='directory',
            data=combined_data,
            ci='sd'
        )
        plt.ylabel(metric)
        plt.legend( loc='upper center', ncol=2)
        plt.tight_layout()
        plt.savefig(os.path.join(visuals_dir, f"combined_{metric}.png"))
        plt.close()
    
if __name__ == "__main__":
    base_dir = "results/report/loss_0.1"
    viz_project(base_dir)
