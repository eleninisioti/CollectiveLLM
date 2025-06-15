import yaml
import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import numpy as np

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
    elif 'mem_mix_act_10' in dir_name:
        return 'mix_10'
    return dir_name[-25:]  # fallback to last 25 chars if no match


def analyse_play(trial_data):
    # we assume only one agent
    cultural_losses = {}
    cultural_gains = {}
    
    in_memory = 0
    in_active_memory = 0
    in_active_keep = []
    in_active_keep = []

    for step in range(1,len(trial_data)):
        
        action = trial_data[step]["actions"]["agent_0"]
        
        active_memories = trial_data[step]["active_memory"]["agent_0"]
        
        for word in action:
            in_active_memory = False
            for memory in active_memories:
                if word == memory[0] or word == memory[1]:
                    in_active_memory = True
            in_active_keep.append(in_active_memory)
            
                    
    in_active = sum([1 for el in in_active_keep if el == True])
    
    # now check if what was played was invalid and if so, whether it was in active memory
    in_memory = 0
    total_invalid = 0
    for step in range(1,len(trial_data)):
        
        action = trial_data[step]["actions"]["agent_0"]
        
        active_memories = trial_data[step]["active_memory"]["agent_0"]
        print(len(active_memories))
        
        valid_attempts = trial_data[step-1]["valid_attempts"]["agent_0"]
        invalid_attempts = trial_data[step-1]["invalid_attempts"]["agent_0"]
        
        if step == 41:
            print("check")
        
        recipe_perm1 = (action[0], action[1])
        recipe_perm2 = (action[1], action[0])
        
        if recipe_perm1 in valid_attempts or recipe_perm2 in valid_attempts:
            in_valid = True
        else:
            in_valid = False
        if recipe_perm1 in invalid_attempts or recipe_perm2 in invalid_attempts:
            in_invalid = True
        else:
            in_invalid = False
                


                
        if in_valid or in_invalid:
            total_invalid += 1
            present = False
            for el in active_memories:
                temp = el[:2]
                if action == el[:2]:
                    present = True
                
            if present:
                in_memory += 1
                
    
    
    metrics = {"chose_in_active": in_active/(len(in_active_keep)+1),
               "not_in_memory": in_memory/(len(in_active_keep)+1)}

    return metrics



def analyse_memory(trial_data):
    # we assume only one agent
    cultural_losses = {}
    cultural_gains = {}
    
    in_memory = 0
    in_active_memory = 0

    for step in range(1,len(trial_data)):
        
        for el in cultural_losses.keys():
            for mem in  trial_data[step]["memory"]["agent_0"]:
                if mem[2] == el:
                    in_memory += 1
                    
            for mem in  trial_data[step-1]["active_memory"]["agent_0"]:
                if mem[2] == el:
                    in_active_memory += 1
                    
                
        step_data = trial_data[step]["inventory"]["agent_0"]
        prev_step_data = trial_data[step-1]["inventory"]["agent_0"]
        lost = [el for el in prev_step_data if el not in step_data]
        
                
                
        for el in lost:
            cultural_losses[el] = step
        for el in cultural_losses.keys():
            if el in step_data:
                cultural_gains[el] = step
            
                
    cultural_times = {}
    for item in cultural_losses.keys():
        if item in cultural_gains.keys():
            cultural_times[item] = cultural_gains[item] - cultural_losses[item]
        else:
            cultural_times[item] = len(trial_data) - cultural_losses[item]
               
    num_losses = len(cultural_losses.keys())
    
    # The error is likely due to np.mean(cultural_times.values()) because in Python 3, dict.values() returns a view, not a list or array.
    # Convert to a list before passing to np.mean.
    lost_time = np.mean(list(cultural_times.values())) 
    
    metrics = {"cultural_loss": num_losses, "lost_time": lost_time}
    return metrics

    
    
    
def viz_metrics(project_dir, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    with open(project_dir + "/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    n_trials = config["num_trials"]
    
    metrics_memory = []
    metrics_play = []

    for trial in range(n_trials):
        with open(project_dir + "/data/log_info_" + str(trial) + ".pkl", "rb") as f:
            trial_data  = pickle.load(f)
            
        #with open(project_dir + "/data/attempts_info_" + str(trial) + ".pkl", "rb") as f:
        #    attempts_data  = pickle.load(f)
        trial_metrics = analyse_memory(trial_data)
        trial_metrics_play = analyse_play(trial_data)

        trial_metrics["trial"] = trial
        #trial_metrics_play["trial"] = trial
        metrics_memory.append(trial_metrics)
        metrics_play.append(trial_metrics_play)
        
    # Convert list of dictionaries to DataFrame
    data = pd.DataFrame(metrics_play)
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
        
        data, metrics = viz_metrics(subdir, os.path.join(subdir, "visuals"))
        all_data.append(data)
        all_metrics.update(metrics)
        #except Exception as e:
        #    print(f"Error processing directory {subdir}: {str(e)}")
    
    if not all_data:
        print("No valid data found in any directory")
        return
        
    # Combine all data
    combined_data = pd.concat(all_data, ignore_index=True)
    
    # Create consolidated plots for each metric
    for metric in all_metrics:
        plt.figure()
        sns.barplot(
            x='directory',
            y=metric,
            data=combined_data,
            ci='sd',  # This will show standard deviation as error bars
            capsize=0.1  # This adds small horizontal lines at the end of error bars
        )
        plt.ylabel(metric)
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        plt.tight_layout()
        plt.savefig(os.path.join(visuals_dir, f"combined_{metric}.png"))
        plt.close()
    
if __name__ == "__main__":
    base_dir = "results/report/loss_0.1"
    viz_project(base_dir)