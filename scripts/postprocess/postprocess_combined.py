import os
import pickle
import yaml
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import glob

fig_size = (8.27/2*2, 11.69/4*2)
plt.rcParams["figure.figsize"] = fig_size
plt.rcParams.update({'font.size': 11})

def get_project_label(project_dir):
    """Extract a meaningful label from the project directory path."""
    # Get the last few parts of the path
    parts = project_dir.split(os.sep)
    # Take the last 3 parts of the path for the label
    label_parts = parts[-3:] if len(parts) >= 3 else parts
    return "_".join(label_parts)

def viz_combined_performance(top_dir, save_dir):
    """Create combined lineplots for all projects."""
    project_dirs = find_project_dirs(top_dir)
    all_data = []
    
    for project_dir in project_dirs:
        # Load config to get number of trials
        with open(os.path.join(project_dir, "config.yaml"), "r") as f:
            config = yaml.safe_load(f)
        n_trials = config["num_trials"]
        
        # Load results for each trial
        project_results = []
        for trial in range(n_trials):
            results_path = os.path.join(project_dir, "data", f"results_{trial}.pkl")
            if os.path.exists(results_path):
                with open(results_path, "rb") as f:
                    trial_results = pickle.load(f)
                    # Add project label to the data
                    trial_results['project'] = get_project_label(project_dir)
                    project_results.append(trial_results)
        
        if project_results:
            all_data.extend(project_results)
    
    if not all_data:
        print("No data found in any project")
        return
    
    # Combine all data
    combined_data = pd.concat(all_data, ignore_index=True)
    
    # Get metrics (excluding non-metric columns)
    metrics = [col for col in combined_data.columns 
              if col not in ['steps', 'trial', 'project']]
    
    # Create plots for each metric
    for metric in metrics:
        plt.figure()
        sns.lineplot(
            x='steps',
            y=metric,
            hue='project',
            data=combined_data,
            ci='sd'
        )
        plt.ylabel(metric)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3)
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, f"combined_{metric}.png"), 
                   bbox_inches='tight', dpi=300)
        plt.close()

def find_project_dirs(top_dir):
    """Recursively find all directories containing config.yaml files."""
    project_dirs = []
    for root, dirs, files in os.walk(top_dir):
        if "config.yaml" in files:
            project_dirs.append(root)
    return project_dirs

if __name__ == "__main__":
    top_dir = "results/report/reproduce_deceptive"
    save_dir = os.path.join(top_dir, "combined_visuals")
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    print(f"Processing all projects in {top_dir}")
    viz_combined_performance(top_dir, save_dir)
    print(f"Combined visualizations saved to {save_dir}") 