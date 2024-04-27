import pickle
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas
import yaml
import numpy as np
import seaborn as sns

custom_palette = ["#ff595e","#ffca3a","#8ac926","#1982c4","#6a4c93"]

# ----- global configuration of plots -----
params = {'legend.fontsize': 14,
          "figure.autolayout": True,
          'font.size': 14,
          #"image.cmap": custom_palette,
          "axes.prop_cycle": plt.cycler(color=custom_palette)}
plt.rcParams.update(params)
cm = 1 / 2.54
scale = 3
fig_size = (3 / scale, 2 / scale)

method_names = {"llama2": "Llama 2",
                "chatgpt": "Gpt-3.5 Turbo",
                "random": "random",
                "empower": "empower",
                "empower_cultural_evo": "empower+copy"}


method_names = {"dynamic": "dynamic",
                "fully-connected": "fully-connected"}

def compare_label(top_dir, trials, parameter, parameter_2, order, label):
    projects = [top_dir + f for f in os.listdir(top_dir) if os.path.isdir(os.path.join(top_dir, f))]

    total_df = pandas.DataFrame(columns=["trial", "step", "model", "mean_reward", "agent"])
    for idx, project in enumerate(projects):
        project_data = []
        for trial in range(trials):

            if os.path.exists(project + "/data/results_" + str(trial) + '.pkl'):
                project_data.append(pickle.load(open(project + "/data/results_" + str(trial) + ".pkl", "rb")))
        results = pandas.concat(project_data)
        config = yaml.load(open(project + "/config.yaml", "r"), Loader=yaml.SafeLoader)

        steps = set(results['global_step'].tolist())
        model = str(config[parameter_2])

        for step in steps:
            step_results = results.loc[results['global_step'] == step]

            trial_values = set(step_results['trial'].tolist())
            task_values = set(step_results['task'].tolist())
            max_values = []
            for trial in trial_values:
                for task in task_values:
                    current_results = step_results.loc[step_results['trial'] == trial]
                    current_results = current_results.loc[current_results['task'] == task]
                    max_values.append(current_results[label].max())
            counterx=0
            for trial in trial_values:
                for task in task_values:
                    current_results = step_results.loc[step_results['trial'] == trial]
                    current_results = current_results.loc[current_results['task'] == task]
                    model_name =  method_names[model]
                    for agent_idx, el in enumerate(current_results[label]):
                        total_df.loc[len(total_df)] = [trial, step, model_name, el, agent_idx ]
                    #try:
                        #total_df.loc[len(total_df)] = [trial, step, model_name,  current_results[label].mean(), np.mean(max_values[counterx])]
                    #except IndexError:
                    #    print(len(max_values), counterx)
                    counterx +=1
    fig, ax = plt.subplots()

    sns.color_palette("tab10")
    sns.lineplot(data=total_df, x='step', y="mean_reward", errorbar="ci", hue="model", hue_order=order)
    # Initialize the figure and axis
    ax.set_ylabel("Copy time")
    ax.set_xlabel('Crafting step')
    #ax.set_xticklabels([method_names[order] for order in order])  # You can customize the tick labels

    # Display the legend
    ax.legend(ncol=1, loc="upper left")

    # Show the plot
    plt.savefig(top_dir + "/compare_" + label + "_mean.pdf")
    plt.clf()

    fig, ax = plt.subplots()

    sns.color_palette("tab10")
    sns.lineplot(data=total_df, x='step', y="max_reward", errorbar="ci", hue="model", hue_order=order)
    # Initialize the figure and axis
    ax.set_ylabel('Reward')
    ax.set_xlabel('Crafting step')
    #ax.set_xticklabels([method_names[order] for order in order])  # You can customize the tick labels

    # Display the legend
    ax.legend(ncol=1, loc="upper left")

    # Show the plot
    plt.savefig(top_dir + "/compare_" + label + "_max.pdf")
    plt.clf()


def openended():
    trials = 10

    targeted_dirs = [
        "results/papers/copy_time/6agents/chatgpt/",
    ]

    order = ["dynamic", "fully-connected"]
    order = [method_names[el] for el in order]

    for top_dir in targeted_dirs:
        compare_label(top_dir, trials, parameter="num_agents", parameter_2="connectivity", order=order, label="copy_time")




if __name__ == "__main__":
    openended()
