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
          'font.size': 16,
          #"image.cmap": custom_palette,
          "axes.prop_cycle": plt.cycler(color=custom_palette)}
plt.rcParams.update(params)
cm = 1 / 2.54
scale = 3
fig_size = (3 / scale, 2 / scale)

method_names = {"llama2": "Llama 2",
                "chatgpt": "Gpt-3.5 Turbo",
                "random": "random",
                "empower": "empower"}

def compare_label(top_dir, trials, parameter, parameter_2, order, label):
    projects = [top_dir + f for f in os.listdir(top_dir) if os.path.isdir(os.path.join(top_dir, f))]

    total_df = pandas.DataFrame(columns=["trial", "step", "model", "mean_reward", "max_reward"])
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
                    try:
                        total_df.loc[len(total_df)] = [trial, step, model_name,  current_results[label].mean(), np.mean(max_values[counterx])]
                    except IndexError:
                        print(len(max_values), counterx)
                    counterx +=1
    fig, ax = plt.subplots()

    sns.color_palette("tab10")
    sns.lineplot(data=total_df, x='step', y="mean_reward", errorbar="ci", hue="model", hue_order=order)
    # Initialize the figure and axis
    ax.set_ylabel('Inventory size')
    ax.set_xlabel('Crafting step')
    #ax.set_xticklabels([method_names[order] for order in order])  # You can customize the tick labels

    # Display the legend
    ax.legend(ncol=1, loc="upper center")

    # Show the plot
    plt.savefig(top_dir + "/compare_" + label + "_mean.png")
    plt.clf()

def compare_reward(top_dir, trials, parameter, parameter_2, order):
    projects = [top_dir + f for f in os.listdir(top_dir) if os.path.isdir(os.path.join(top_dir, f))]

    total_df = pandas.DataFrame(columns=["trial", "step", "model", "mean_reward", "max_reward"])
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
                    max_values.append(current_results['reward'].max())
            counterx=0
            for trial in trial_values:
                for task in task_values:
                    current_results = step_results.loc[step_results['trial'] == trial]
                    current_results = current_results.loc[current_results['task'] == task]
                    model_name =  method_names[model]
                    try:
                        total_df.loc[len(total_df)] = [trial, step, model_name,  current_results['reward'].mean(), np.mean(max_values[counterx])]
                    except IndexError:
                        print(len(max_values), counterx)
                    counterx +=1
    fig, ax = plt.subplots()

    sns.color_palette("tab10")
    sns.lineplot(data=total_df, x='step', y="mean_reward", errorbar="ci", hue="model", hue_order=order)
    # Initialize the figure and axis
    ax.set_ylabel('Inventory size')
    ax.set_xlabel('Crafting step')
    ax.set_ylim(0, 48)
    #ax.set_xticklabels([method_names[order] for order in order])  # You can customize the tick labels

    # Display the legend
    ax.legend(ncol=2, loc="upper center")

    # Show the plot
    plt.savefig(top_dir + "/compare_reward_mean.pdf")
    plt.clf()




def compare_success(top_dir, trials, parameter, parameter_2, order):
    projects = [top_dir + f for f in os.listdir(top_dir) if os.path.isdir(os.path.join(top_dir, f))]

    fig, ax = plt.subplots()

    results = {}
    for idx, project in enumerate(projects):
        project_data = []
        if "chatgpt" in project:
            trials = 3
        for trial in range(trials):

            if os.path.exists(project + "/data/results_" + str(trial) + '.pkl'):
                project_data.append(pickle.load(open(project + "/data/results_" + str(trial) + ".pkl", "rb")))

        output = pandas.concat(project_data)
        config = yaml.load(open(project + "/config.yaml", "r"), Loader=yaml.SafeLoader)
        last_step = config["num_steps"] - 1
        converged_results = output.loc[output['global_step'] == last_step]
        mean_value = converged_results['success'].mean()
        variance_value = converged_results['success'].var()
        # find maximum among agents averaged across trials and tasks
        trial_values = set(converged_results['trial'].tolist())
        task_values = set(converged_results['task'].tolist())
        task_values = range(50)
        max_values = []
        for trial in trial_values:
            for task in task_values:
                current_results = converged_results.loc[converged_results['trial'] == trial]
                current_results = current_results.loc[current_results['task'] == task]
                max_values.append(current_results['success'].max())

        max_value = np.mean(max_values)

        results[str(config[parameter_2])] = (mean_value, variance_value, max_value)

    # Initialize the figure and axis
    fig, ax = plt.subplots()
    #colormap = plt.cm.get_cmap(
    #    'Set2')  # You can choose any colormap from Matplotlib    # Plotting the mean values as bars
    bars = ax.bar(range(len(order)), [results[label][0] for label in order], align='center',
                  color=[custom_palette[idx] for idx in range(len(order))]
                  #color=colormap(np.arange(len(order)))
                  )
    # Plotting the variance values as bars next to the mean values
    # ax.bar([i + 0.4 for i in range(len(projects))], variance_values, width=0.4, label='Variance', align='center')
    print(top_dir)
    for i, bar in enumerate(bars):
        label = order[i]
        print(bar.get_height(),  results[label][1])
        plt.vlines(x=i, ymin=bar.get_height() - results[label][1] / 2,
                   ymax=bar.get_height() + results[label][1] / 2, color='black', linewidth=2)

    # Adding labels and title

    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([method_names[order] for order in order])  # You can customize the tick labels
    ax.set_ylabel('Success')
    ax.set_xlabel('')
    ax.set_ylim([0,1])

    # Display the legend
    #ax.legend(ncol=3)

    # Show the plot
    plt.savefig(top_dir + "/compare_success.pdf", dpi=500)
    plt.clf()



def targeted():
    trials = 10

    targeted_dirs = [
        "results/papers/targeted/1level/3distractors/",
        "results/papers/targeted/1level/6distractors/",
        "results/papers/targeted/2level/3distractors/",
        "results/papers/targeted/2level/6distractors/",

    ]

    order = ["random", "empower", "llama2", "chatgpt"]

    for top_dir in targeted_dirs:
        compare_success(top_dir, trials, parameter="num_agents", parameter_2="model_name", order=order)


def openended():
    trials = 10

    targeted_dirs = [
        "results/papers/openended/parametric/openended/",

    ]

    order = ["random", "empower", "llama2", "chatgpt"]
    order = [method_names[el] for el in order]

    for top_dir in targeted_dirs:
        compare_reward(top_dir, trials, parameter="num_agents", parameter_2="model_name", order=order)

    targeted_dirs = [
        "results/papers/openended/parametric/openended_with_explore/",

    ]

    order = ["random", "empower", "chatgpt"]
    order = [method_names[el] for el in order]
    label = "perc_explore"

    for top_dir in targeted_dirs:
        compare_label(top_dir, trials, parameter="num_agents", parameter_2="model_name", order=order, label=label)

    label = "perc_explore_meaning"

    for top_dir in targeted_dirs:
        compare_label(top_dir, trials, parameter="num_agents", parameter_2="model_name", order=order, label=label)


if __name__ == "__main__":
    targeted()
    #openended()
