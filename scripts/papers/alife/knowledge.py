from scipy.stats import f_oneway
import pickle
import os
import gym
import os, sys
import numpy as np
from collections import defaultdict
sys.path.append(os.getcwd())
sys.path.append(os.getcwd()+"/wordcraft")
print(sys.path)
import gensim.downloader
import math
glove_vectors = gensim.downloader.load('glove-twitter-25')


#with open("glove_vectors.pkl", "rb") as f:
#    glove_vectors = pickle.load( f)



def compute_sims():
    pass


def compare_sims():
    # load chatgpt data
    with open("results/papers/knowledge/chatgpt.txt", 'r') as file:
        results = file.readlines()
        chatgpt_sims = []
        for step in results[1:]:
            step_results = step.split()
            chatgpt_sims.append(float(step_results[2]))

    # load empower data
    os.chdir("wordcraft")
    print(os.getcwd())
    from wordcraft_openended.env import WordCraftEnv
    from wordcraft_openended.recipe_book import Recipe, RecipeBook

    env = gym.make(
        'wordcraft-multistep-goal-v0',
        encoded=False,
        max_mix_steps=201,
        seed=0)
    os.chdir("..")
    trials = 10
    results_dir = "results/papers/knowledge/random"
    correct_words = []
    for trial in range(trials):
        with open("results/papers/openended/single/empower/data/results_" + str(trial) + ".pkl", "rb") as f:
            empower_results = pickle.load(f)
            empower_words = empower_results["action_words"].tolist()
            for step in range(200):
                action = empower_results.loc[empower_results['global_step']==step]["action_words"].tolist()[0]
                actions = action.split()
                recipe = Recipe(actions)
                correct_word = env.env.env.recipe_book.recipe2entity[recipe]
                correct_words.append(correct_word)


    # load dummy data
    trials = 10
    results_dir = "results/papers/knowledge/random"
    dummy_sims_total = defaultdict(list)
    for trial in range(trials):

        with open(results_dir + "/data/results_" + str(trial) + ".pkl", "rb") as f:
            results = pickle.load(f)
            words = results["action_words"].tolist()
            for step in range(200):
                word = words[step].split()
                try:
                    sim = glove_vectors.similarity(word[0], correct_words[step])

                    dummy_sims_total[step].append(sim)

                except KeyError:
                    print(word[0] + " does not exist")
            print("check")
    dummy_sims = []
    for el in range(100):
        dummy_sims.append(np.mean(dummy_sims_total[el]))


    trials = 10
    results_dir = "results/papers/knowledge/llama2"
    llama_sims_total = defaultdict(list)
    for trial in range(trials):

        with open(results_dir + "/data/results_" + str(trial) + ".pkl", "rb") as f:
            results = pickle.load(f)
            words = results["action_words"].tolist()
            for step in range(200):
                word = words[step].split()
                try:
                    sim = glove_vectors.similarity(word[0], correct_words[step])

                    llama_sims_total[step].append(sim)

                except KeyError:
                    print(word[0] + " does not exist")
            print("check")
    llama_sims = []
    for el in range(100):
        llama_sims.append(np.mean(dummy_sims_total[el]))

    # load llama2 data

    chatgpt_sims = [x for x in chatgpt_sims if not (isinstance(x, float) and math.isnan(x))]
    dummy_sims = [x for x in dummy_sims if not (isinstance(x, float) and math.isnan(x))]
    llama_sims = [x for x in llama_sims if not (isinstance(x, float) and math.isnan(x))]


    print("chatgpt mean", np.mean(chatgpt_sims))
    print("dummy mean", np.mean(dummy_sims))
    print("chatgpt mean", np.mean(llama_sims))


    anova = f_oneway(chatgpt_sims,   llama_sims)
    print(anova)
    print("check")


if __name__ == "__main__":
    compare_sims()