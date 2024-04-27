import pandas
import seaborn as sns
import matplotlib.pyplot as plt
import os
import pickle
import yaml
import shutil
top_dir = "results/reports/26_10_2023/openended/1agent/"
top_dir = "results/papers/openended/parametric/openended/"
top_dir = "results/2024_04_10/"

trials = 10
projects = [top_dir + f for f in os.listdir(top_dir) if os.path.isdir(os.path.join(top_dir, f))]
failed_projects = []

# load results
for project in projects:

    data = []
    if os.path.exists(project + "/data/results_0.pkl"):

        for trial in range(trials):
            if os.path.exists(project + "/data/results_" + str(trial) + ".pkl"):
                data.append(pickle.load(open(project + "/data/results_" + str(trial) + ".pkl", "rb")))
        results = pandas.concat(data)

        config = yaml.load(open(project + "/config.yaml", "r"), Loader=yaml.SafeLoader)

        #  -----agent-specific plots ------
        metrics = ["steps",
                   "invalid_attempts",
                   "success",
                   "count_repeated_valid",
                   "count_repeated_invalid",
                   "count_double_action",
                   "count_repeated_valid_other",
                   "count_repeated_invalid_other", "reward",
                   "inventory_length","copy_time"
                   ]

        for agent_idx in range(config["num_agents"]):
            plots_dir = project + "/plots/agent_" + str(agent_idx)
            if not os.path.exists(plots_dir):
                os.makedirs(plots_dir)

            results_agent = results.loc[results['agent'] == agent_idx]

            for metric in metrics:

                if metric == "reward" or metric == "inventory_length" or metric == "copy_time":
                    sns.lineplot(data=results_agent, x='global_step', y=metric, errorbar="ci")
                else:
                    last_step = config["num_steps"]-1
                    converged_results = results_agent.loc[results_agent['global_step'] == last_step]
                    if metric == "success":
                        sns.barplot(data=converged_results, x='task', y=metric,errorbar=None)
                    else:
                        sns.barplot(data=converged_results, x='task', y=metric, errorbar="ci")

                plt.savefig(plots_dir + "/" + metric + ".png")
                plt.clf()
        # ------------------------------
        # --- population-average plots ---
        plots_dir = project + "/plots"
        for metric in metrics:
            if metric == "reward" or metric == "inventory_length" or metric == "copy_time":
                sns.lineplot(data=results, x='global_step', y=metric, errorbar="ci")
            else:

                converged_results = results.loc[results['global_step'] == last_step]
                if metric == "success"  :

                    sns.barplot(data=converged_results, x='task', y=metric, errorbar=None)
                else:
                    sns.barplot(data=converged_results, x='task', y=metric, errorbar="ci")

            plt.savefig(plots_dir + "/" + metric + ".png")
            plt.clf()
        # ------------------------------
    else:
        failed_projects.append(project)

for el in failed_projects:
    print(el + "\n")
print(len(failed_projects))





