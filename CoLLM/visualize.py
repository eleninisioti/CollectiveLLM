import yaml
import pickle
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
# ----- general figure configuration -----
cm = 1 / 2.54  # inches to cm
scale = 1
width, height = 3, 2
fig_size = (width / scale / cm, height / scale / cm)
params = {'legend.fontsize': 10,
          "figure.autolayout": True,
          'font.size': 10,
          "figure.figsize": fig_size}
plt.rcParams.update(params)


colormap = {
        0: ['#ffadad', '#ff5858', '#ff0202', '#ab0000', '#560000'],
        1: ['#bdb2ff', '#745cff', '#2b05ff', '#1a00ad', '#0d0057'],
        2: ['#fdffb6', '#faff60', '#f7ff08', '#aaaf00', '#555800'],
        3: ['#caffbf', '#7eff64', '#34ff0b', '#1eb100', '#0f5900'],
        4: ['#9bf6ff', '#47f0ff', '#00e0f5', '#0096a3', '#004b52'],
        5: ['#a0c4ff', '#4b90ff', '#005ff8', '#003fa5', '#002053'],
        6: ['#ffd6a5', '#ffb050', '#fb8a00', '#a75c00', '#542e00'],
        7: ['#ffc6ff', '#ff6cff', '#ff11ff', '#b600b6', '#5b005b'],
        8: ['#fffffc', '#ffff95', '#ffff30', '#caca00', '#656500']
    }

all_colors = [color for colors in colormap.values() for color in colors]
def viz_success(project_dir, n_trials, task_length):
    save_dir = project_dir + "/visuals"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    data = []
    for trial in range(n_trials):
        with open(project_dir + "/data/results_" + str(trial) + ".pkl", "rb") as f:
            data.append(pickle.load(f))

    data = pd.concat(data, ignore_index=True)

    data_conv = data[data["steps"]==task_length-1]

    # ----- plot average across tasks and population -----
    plt.figure(figsize=fig_size)
    sns.barplot(
        x='task',
        y='success',
        data=data_conv,
        ci='sd',  # Use standard deviation for error bars
        palette=all_colors)
    plt.ylim(bottom=0)  # Set the lower limit of the y-axis to 0
    #    plt.xlabel('Task')
    plt.ylabel('Success (average across trials and group)')
    plt.savefig(save_dir + "/sucess_avg.png")
    plt.clf()

    # ----- plot maximum within population-----

    # Compute the maximum success for each task and trial
    max_success_per_trial = data_conv.groupby(['task', 'trial'])['success'].max().reset_index()

    # Compute the average of these maximum values across trials for each task
    average_max_success = max_success_per_trial.groupby('task')['success'].mean().reset_index()

    plt.figure(figsize=(10, 6))

    sns.barplot(
        x='task',
        y='success',
        data=average_max_success,
        ci='sd',  # Use standard deviation for error bars
        palette=all_colors
    )

    plt.ylim(bottom=0)

    plt.xlabel('Task')
    plt.ylabel('Success (average across trials and maximum within group)')
    plt.savefig(save_dir + "/sucsess_max.png")
    plt.clf()


def viz_inventory(project_dir, n_trials, task_length):
    save_dir = project_dir + "/visuals"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    data = []
    for trial in range(n_trials):
        with open(project_dir + "/data/results_" + str(trial) + ".pkl", "rb") as f:
            data.append(pickle.load(f))

    data = pd.concat(data, ignore_index=True)

    # ----- plot average across tasks and population -----
    plt.figure(figsize=fig_size)
    sns.lineplot(
        x='steps',
        y='inventory_length',
        data=data,
        ci='sd',  # Use standard deviation for error bars
        palette=all_colors)
    #    plt.xlabel('Task')
    plt.ylabel('Success (average across trials and group)')
    plt.savefig(save_dir + "/inventory_avg.png")
    plt.clf()

    # ----- plot maximum within population-----

    # Compute the maximum success for each task and trial
    max_success_per_trial = data.groupby(['steps', 'trial'])['inventory_length'].max().reset_index()

    # Compute the average of these maximum values across trials for each task
    average_max_success = max_success_per_trial.groupby('steps')['inventory_length'].mean().reset_index()

    plt.figure(figsize=fig_size)
    sns.lineplot(
        x='steps',
        y='inventory_length',
        data=average_max_success,
        ci='sd',  # Use standard deviation for error bars
        palette=all_colors)

    plt.xlabel('Task')
    plt.ylabel('Success (average across trials and maximum within group)')
    plt.savefig(save_dir + "/inventory_max.png")
    plt.clf()

def viz_project(project_dir):
    with open(project_dir + "/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    if config["openended"]:
        viz_inventory(project_dir, n_trials=config["num_trials"], task_length=config["num_steps"])
    else:
        viz_success(project_dir, n_trials=config["num_trials"], task_length=config["num_steps"])


