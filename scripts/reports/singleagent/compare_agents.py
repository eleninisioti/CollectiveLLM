import pickle
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas
import yaml
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from collections import defaultdict

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


def regression(top_dir, trials):
    projects = [top_dir + f for f in os.listdir(top_dir) if os.path.isdir(os.path.join(top_dir, f))]


    for project in projects:

        config = yaml.safe_load(open(project + "/config.yaml", "r"))

        method = config["model_name"]
        data = []
        if os.path.exists(project + "/data/results_0.pkl"):

            for trial in range(trials):
                if os.path.exists(project + "/data/results_" + str(trial) + ".pkl"):
                    method_data = pickle.load(open(project + "/data/results_" + str(trial) + ".pkl", "rb"))
                    method_data["method"] = method
                    method_data["trial"] = trial
                    data.append(method_data)
        results = pandas.concat(data)


        results = results[["trial", "agent", "global_step", "action_words", "method"]]

        column_data = results[['action_words']]

        # Initialize OneHotEncoder
        encoder = OneHotEncoder()

        # Fit and transform the data
        onehot_encoded = encoder.fit_transform(column_data)

        #maybe try this instead
        #single_column_encoded = pandas.get_dummies(data=results[['action_words']], drop_first=True)

        # Convert the sparse matrix to a dense array
        onehot_encoded_array = onehot_encoded.toarray()

        # Concatenate the one-hot encoded array as a single column
        single_column_encoded = np.argmax(onehot_encoded_array, axis=1)

        # Add the single column encoding as a new column in the DataFrame
        results['action_words'] = single_column_encoded
        for trial in range(trials):
            results_trial = results[results["trial"] == trial]
            coeffs = defaultdict(list)
            for method in results["method"].unique():

                for method2 in results["method"].unique():

                    y = results_trial[results_trial["method"] == method]
                    x = results_trial[results_trial["method"] == method2]

                    y = pandas.DataFrame(y["action_words"])
                    x = pandas.DataFrame(x["action_words"])

                    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

                    # Initialize logistic regression model
                    model = LogisticRegression()

                    # Fit logistic regression model
                    model.fit(X_train, y_train)

                    # Get regression coefficients
                    coefficients = model.coef_[0]

                    coeffs[method].append((method2, float(coefficients)))

                ## do what i did for pnas, anova and bonferonni correction. I basically want to compare all with all
            print(coeffs)

        for method, values in coeffs.items():
            fig, ax = plt.subplots()
            other_methods = [method for method, coeff in values]
            coeffs = [coeff for method, coeff in values]

            ax.bar(other_methods ,coeffs, width=0.4, align='center')
            plt.savefig(top_dir + "/regression_" + method + ".png")
            plt.clf()

        print("check")
def openended():
    trials = 100


    targeted_dirs = [
        "results/reports/singleagent/openended/",
    ]

    order = ["random", "uncertainty", "empower"]

    for top_dir in targeted_dirs:
        compare_reward(top_dir, trials, parameter="num_agents", parameter_2="model_name", order=order)


def targeted():
    trials = 10

    targeted_dirs = [
        #"results/reports/singleagent/targeted/1level/3distractors/",
        "results/reports/singleagent/targeted/1level/6distractors/",
        "results/reports/singleagent/targeted/2level/3distractors/",
        #"results/reports/singleagent/targeted/2level/6distractors/",
    ]

    order = ["random", "uncertainty", "empower", "llama2", "chatgpt"]

    for top_dir in targeted_dirs:
        compare_success(top_dir, trials, parameter="num_agents", parameter_2="model_name", order=order)



if __name__ == "__main__":
    targeted()