import os
import pickle
import yaml
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import glob


fig_size = (8.27/2*2, 11.69/4*2)  # A4 column width in inches (portrait orientation)
plt.rcParams["figure.figsize"] = fig_size
plt.rcParams.update({'font.size': 11})


def viz_performance(project_dir, save_dir, n_trials):
    all_results = []
    for trial in range(n_trials):
        results_path = os.path.join(project_dir, "data", f"results_{trial}.pkl")
        if os.path.exists(results_path):
            with open(results_path, "rb") as f:
                trial_results = pickle.load(f)
                all_results.append(trial_results)
                
                # Save trial results to text file
                txt_path = os.path.join(project_dir, "data", f"results_{trial}.txt")
                with open(txt_path, "w") as txt_file:
                    txt_file.write(str(trial_results))
    
    data = pd.concat(all_results, ignore_index=True)
    
    # Save DataFrame to CSV file
    csv_path = os.path.join(save_dir, "combined_results.csv")
    data.to_csv(csv_path, index=False)

    
    metrics = [col for col in all_results[0].columns if col != 'steps' and col != 'trial']

    for metric in metrics:    
        plt.figure()
        sns.lineplot(
            x='steps',
            y=metric,
            data=data,
            ci='sd'
        )
        plt.ylabel(metric)
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, metric + ".png"))
        plt.close()
        
        plt.figure()
        sns.lineplot(
            x='steps',
            y=metric,
            data=data,
            estimator="max",
            ci='sd'
        )
        plt.ylabel(metric)
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, metric + "_max.png"))
        plt.close()


def viz_cultural_loss(project_dir, save_dir, n_trials, num_steps):
    metrics = []
    
    for trial in range(n_trials):
        results_path = os.path.join(project_dir, "data", f"log_info_{trial}.pkl")
        if os.path.exists(results_path):
            with open(results_path, "rb") as f:
                trial_data = pickle.load(f)
                
                
                # we assume only one agent
                cultural_losses = {}
                cultural_gains = {}
                

                for step in range(1,len(trial_data)):
                                         
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
                        cultural_times[item] = num_steps - cultural_losses[item]
                        
                num_losses = len(cultural_losses.keys())
                
                # The error is likely due to np.mean(cultural_times.values()) because in Python 3, dict.values() returns a view, not a list or array.
                # Convert to a list before passing to np.mean.
                lost_time = np.mean(list(cultural_times.values())) 
                
                metrics.append([num_losses, lost_time, trial])
                
    data = pd.DataFrame(metrics, columns=["num_losses", "lost_time", "trial"])
    metrics = ["num_losses", "lost_time"]
    for metric in metrics:    
        plt.figure()
        sns.barplot(
            y=metric,
            data=data,
            ci='sd',  # This will show standard deviation as error bars
            capsize=0.1  # This adds small horizontal lines at the end of error bars
        )

        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, metric + ".png"))
        plt.close()
        
        
def viz_memory(project_dir, save_dir, n_trials, num_steps):
    metrics = []
    
    for trial in range(n_trials):
        results_path = os.path.join(project_dir, "data", f"log_info_{trial}.pkl")
        if os.path.exists(results_path):
            with open(results_path, "rb") as f:
                trial_data = pickle.load(f)
                
                    
                in_memory = 0
                in_active_memory = 0
                in_active_keep = []
                in_active_keep = []
                
                
                # is the agent choosing items that are in its active memory?
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
                
                # is the agent repeating valid and invalid combinations only when they are not in its active memory?

                in_memory = 0
                total_invalid = 0
                for step in range(1,len(trial_data)):
                    
                    action = trial_data[step]["actions"]["agent_0"]
                    active_memories = trial_data[step]["active_memory"]["agent_0"]
                    valid_attempts = trial_data[step-1]["valid_attempts"]["agent_0"]
                    invalid_attempts = trial_data[step-1]["invalid_attempts"]["agent_0"]
                       
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
                            if list(action )== el[:2]:
                                present = True
                            
                        if present:
                            in_memory += 1
                            
                
                metrics.append([in_active/(len(in_active_keep)+1), in_memory/(num_steps), trial ])
                
    data = pd.DataFrame(metrics, columns=["played_in_active", "repeated_in_active", "trial"])
    metrics = ["played_in_active", "repeated_in_active"]
    for metric in metrics:    
        plt.figure()
        sns.barplot(
            y=metric,
            data=data,
            ci='sd',  # This will show standard deviation as error bars
            capsize=0.1  # This adds small horizontal lines at the end of error bars
        )

        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, metric + ".png"))
        plt.close()

        
def postprocess_project(project_dir):
    save_dir = os.path.join(project_dir, "visuals")

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Load config to get number of trials
    with open(os.path.join(project_dir, "config.yaml"), "r") as f:
        config = yaml.safe_load(f)
    n_trials = config["num_trials"]
    num_steps = config["num_steps"]
    # Load results for each trial
    viz_performance(project_dir, save_dir, n_trials)
    
    viz_cultural_loss(project_dir, save_dir, n_trials, num_steps)
    viz_memory(project_dir, save_dir, n_trials, num_steps)


def find_project_dirs(top_dir):
    """Recursively find all directories containing config.yaml files."""
    project_dirs = []
    for root, dirs, files in os.walk(top_dir):
        if "config.yaml" in files:
            project_dirs.append(root)
    return project_dirs


if __name__ == "__main__":
    top_dir = "results/2025_07_05"
    #top_dir = "results/report/reproduce_deceptive_empower"
    project_dirs = find_project_dirs(top_dir)
    for project_dir in project_dirs:
        print(f"Processing {project_dir}")
        postprocess_project(project_dir)
