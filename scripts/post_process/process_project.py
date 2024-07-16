import pickle
import numpy as onp
import os
import csv


def export_messages(project_dir):

    num_agents = 6
    trial = 0
    agent_files = [project_dir + "/logs/trial_" + str(trial) + "/task_0/agent_" +str(agent) for agent in range(num_agents)]

    group_lines = []
    for file in agent_files:
        try:
            with open(file + "/game.txt", 'r') as file:
                lines = [line.strip() for line in file]
            group_lines.append(lines)
        except FileNotFoundError:
            print("The file was not found.")
        except IOError:
            print("An IOError occurred.")

    processed_lines = [0]*num_agents
    for agent_idx, agent_lines in enumerate(group_lines):
        processed_lines[agent_idx] = []
        current_agent_lines = []
        for line_idx, line in enumerate(agent_lines):
            if ("Reasoning" in line):
                current_agent_lines.append(line)
            if ("Combination" in line):
                current_agent_lines.append(line)
                try:

                    processed_lines[agent_idx].append(current_agent_lines[0] + " " + current_agent_lines[1])
                except IndexError:

                    print("skip line")
                current_agent_lines = []


    num_steps = min([len(el) for el in processed_lines])


    final_text = []
    for step in range(num_steps):
        for agent in range(num_agents):
            final_text.append("Agent "+ str(agent)  + ": " + processed_lines[agent][step])

    save_dir = project_dir + "/post_process"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    with open(save_dir + '/dialogue.txt', 'w') as file:
        for line in final_text:
            file.write(line + '\n')



def export_perf(project_dir):
    # load data
    data_file = project_dir + "/data/results_0.pkl"

    with open(data_file, "rb") as f:
        data = pickle.load(f)


    num_steps = set(data["steps"].tolist())

    max_perfs = []
    mean_perfs = []

    for step in num_steps:
        step_perfs = data[data["steps"] == step]["inventory_length"].tolist()

        max_perfs.append(onp.max(step_perfs))
        mean_perfs.append(onp.mean(step_perfs))

    save_dir = project_dir + "/post_process"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    with open(save_dir + "/mean_perfs.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        for item in mean_perfs:
            writer.writerow([item])


    with open(save_dir + "/max_perfs.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        for item in max_perfs:
            writer.writerow([item])




if __name__ == "__main__":

    project_dir = "results/2024_07_13/fully"
    export_perf(project_dir)

    #project_dir = "results/2024_07_13/num_trials_3_num_tasks_1_num_steps_200_openended_True_encoded_False_num_distractors_6_depth_1_agent_type_llama3_forbid_repeats_False_retry_6_temperature_1_top_p_0.9_num_agents_6_connectivity_fully-connected_visit_duration_5_visit_prob_0.1_70B"

    #export_messages(project_dir)

    #project_dir = "results/2024_07_13/num_trials_3_num_tasks_1_num_steps_200_openended_True_encoded_False_num_distractors_6_depth_1_agent_type_llama3_forbid_repeats_False_retry_6_temperature_1_top_p_0.9_num_agents_6_connectivity_dynamic_visit_duration_5_visit_prob_0.1_70B"

    #export_messages(project_dir)

