import pickle
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas
import yaml
import seaborn as sns

def compare_success(top_dir, trials, parameter, parameter_2, order):
    projects = [top_dir + f for f in os.listdir(top_dir) if os.path.isdir(os.path.join(top_dir, f))]

    fig, ax = plt.subplots()

    results = {}
    for idx, project in enumerate(projects):
        project_data = []
        if "chatgpt" in project:
            trials = 1
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
        task_values = range(10)
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
    colormap = plt.cm.get_cmap(
        'tab10')  # You can choose any colormap from Matplotlib    # Plotting the mean values as bars
    bars = ax.bar(range(len(order)), [results[label][0] for label in order],width=0.4, align='center', color=colormap(np.arange(len(order))))
    # Plotting the variance values as bars next to the mean values
    #ax.bar([i + 0.4 for i in range(len(projects))], variance_values, width=0.4, label='Variance', align='center')
    for i, bar in enumerate(bars):
        label = order[i]
        plt.vlines(x=i, ymin=bar.get_height() - results[label][1] / 2,
               ymax=bar.get_height() + results[label][1] / 2, color='black', linewidth=2)


    # Adding labels and title
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(order)  # You can customize the tick labels
    ax.set_ylabel('Value')
    ax.set_xlabel(parameter_2)
    ax.set_title(parameter + '=' + str(config[parameter]) + ', Mean Success ')

    # Display the legend
    ax.legend(ncol=3)

    # Show the plot
    plt.savefig(top_dir + "/compare_success.png")
    plt.clf()

    fig, ax = plt.subplots()

    bars = ax.bar(range(len(order)), [results[label][2] for label in order],width=0.4, align='center', color=colormap(np.arange(len(order))))
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(order)
    ax.set_ylabel('Success')
    ax.set_xlabel(parameter_2)
    num_agents = config['num_agents']
    ax.set_title(parameter + '=' + str(config[parameter]) + ', Max Success')

    # Display the legend
    ax.legend(ncol=3)

    # Show the plot
    plt.savefig(top_dir + "/compare_success_max.png")
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
                    total_df.loc[len(total_df)] = [trial, step, model,  current_results['reward'].mean(), np.mean(max_values[counterx])]

                    counterx +=1
    fig, ax = plt.subplots()

    sns.color_palette("tab10")
    sns.lineplot(data=total_df, x='step', y="mean_reward", errorbar="ci", hue="model", hue_order=order)
    # Initialize the figure and axis
    ax.set_ylabel('Reward')
    ax.set_xlabel('step')
    ax.set_title(parameter + '=' + str(config[parameter]) + ', Mean Reward ')
    # Display the legend
    ax.legend(ncol=3)

    # Show the plot
    plt.savefig(top_dir + "/compare_reward_mean.png")
    plt.clf()


    fig, ax = plt.subplots()
    sns.lineplot(data=total_df, x='step', y="max_reward", errorbar="ci", hue="model", hue_order=order)
    # Initialize the figure and axis
    ax.set_ylabel('Reward')
    ax.set_xlabel(parameter_2)
    ax.set_title(parameter + '=' + str(config[parameter]) + ', Max Reward ')

    # Display the legend
    ax.legend(ncol=3)

    # Show the plot
    plt.savefig(top_dir + "/compare_reward_max.png")
    plt.clf()

def find_sims(project1, project2, trials, tasks, steps, num_agents):
    to_average = []

    for trial in range(trials):
        project1_dir = project1 + "/data/results_" + str(trial) + ".pkl"
        with open(project1_dir , "rb") as f:
            results1 = pickle.load(f)

        project2_dir = project2 + "/data/results_" + str(trial) + ".pkl"
        with open(project2_dir, "rb") as f:
            results2 = pickle.load(f)

        for task in range(tasks):

            task_results1 = results1.loc[results1['task'] == task]
            task_results2 = results2.loc[results2['task'] == task]
            sims = 0

            for step in range(steps):
                step_results1 = task_results1.loc[results1['global_step'] == step]
                step_results2 = task_results2.loc[results2['global_step'] == step]
                actions1 = step_results1["action"].tolist()[0]
                actions2 = step_results2["action"].tolist()[0]

                if actions1 == actions2:
                        sims += 1
            to_average.append(sims/steps)
    return np.mean(to_average)



def compare_behavior(top_dir, trials, parameter, parameter_2):
    projects = [top_dir + f for f in os.listdir(top_dir) if os.path.isdir(os.path.join(top_dir, f))]
    total_sims = {}
    trials = 1
    for project1 in projects:
        for project2 in projects:
            if project1 != project2:
                config1 = yaml.load(open(project1 + "/config.yaml", "r"), Loader=yaml.SafeLoader)
                config2 = yaml.load(open(project2 + "/config.yaml", "r"), Loader=yaml.SafeLoader)
                tasks = config1["num_tasks"]
                steps = config1["num_steps"]
                num_agents = config1["num_agents"]


                key = str(config1[parameter_2]) + " and " + str(config2[parameter_2])
                key_reverse = str(config2[parameter_2]) + " and " + str(config1[parameter_2])
                if key not in total_sims.keys() and key_reverse not in total_sims.keys():
                    total_sims[key] = find_sims(project1, project2, trials, tasks, steps, num_agents)
    order = list(total_sims.keys())
    order.sort()

    plt.bar(range(len(total_sims)), [total_sims[el] for el in order])
    plt.xticks(range(len(total_sims)), order, fontsize=8, rotation=90)
    plt.title(parameter + '=' + str(config1[parameter]) + ', Behavioral similarity')
    plt.tight_layout()

    plt.savefig(top_dir + "/compare_actions.png")
    plt.clf()



def main():
    trials = 1

    # first create barplots of success for targetd tasks

    targeted_dirs = [
        "results/reports/26_10_2023/targeted/1level/",
        "results/reports/26_10_2023/targeted/2level/"

    ]

    order = ["random", "uncertainty", "empower", "empower_onestep", "OA", "chatgpt"]


    for top_dir in targeted_dirs:
        compare_success(top_dir, trials, parameter="num_agents", parameter_2="model_name", order=order)
        #compare_behavior(top_dir, trials, parameter="num_agents", parameter_2="model_name")

    """
    targeted_dirs = [

        "results/reports/26_10_2023/openended/1agent/"

    ]

    order = ["random", "uncertainty", "empower", "empower_onestep", "chatgpt"]


    for top_dir in targeted_dirs:
        compare_reward(top_dir, trials, parameter="num_agents", parameter_2="model_name", order=order)
        compare_behavior(top_dir, trials, parameter="num_agents", parameter_2="model_name")

    """
    targeted_dirs = [
        "results/reports/25_10_2023/openended/6agents/fully/",

    ]

    order = ["random", "uncertainty","empower", "empower_onestep", "chatgpt" ]

    for top_dir in targeted_dirs:
        compare_reward(top_dir, trials, parameter="num_agents", parameter_2="model_name", order=order)
        #compare_behavior(top_dir, trials, parameter="num_agents", parameter_2="model_name")

    """
    targeted_dirs = [
       # "results/reports/25_10_2023/openended/dynamic/chatgpt/",
        #"results/reports/25_10_2023/targeted/2level/chatgpt/",
        #"results/reports/26_10_2023/targeted/1level_chatgpt/",
        "results/reports/26_10_2023/targeted/2level_chatgpt/",

    ]

    order = [ "1", "2", "3" ]

    for top_dir in targeted_dirs:
        compare_success(top_dir, trials, parameter="model_name", parameter_2="num_agents", order=order)
        compare_behavior(top_dir, trials, parameter="model_name", parameter_2="num_agents")

    """
    targeted_dirs = [
        "results/reports/26_10_2023/openended/1agent/",

    ]

    order = ["random", "uncertainty", "empower", "empower_onestep", "OA", "chatgpt"]


    for top_dir in targeted_dirs:
        compare_reward(top_dir, trials, parameter="num_agents", parameter_2="model_name", order=order)
        compare_behavior(top_dir, trials, parameter="num_agents", parameter_2="model_name")

if __name__ == "__main__":
    main()