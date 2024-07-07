# `CoLLM` Collectives of Large Language Models

This is the code accompanying our paper "Collective innovation with Large Language Models", to be presented at the ALife 2024 conference.

`CoLLM` is a framework for running a collective of LLMs on a text environment. You can configure a collective by choosing:

* an LLM (currently support for chatGPT and ollama)
* a group size and connectivity (currently either fully-connected or dynamic)

`CoLLM` is designed to be compatible with different text environments but for now we have only tested in on LittleAlchemy2Text](https://github.com/eleninisioti/LittleAlchemy2Text), a text-based version of the game Little Alchemy 2.

## How does the collective work?
Each agent in the collective has its own copy of the environment.
At each step, agents in a collective play one after the other after observing the state provided by the environment.
Even though agents are identical and have identical environments, they may produce different outputs due to choosing different actions.
Agents affect each other only through the prompt: information about the state of one's neighbors is appended to the prompt of each agent.


## How to use

### Installing dependencies

We have tested our code on Linux and Mac with Python version 3.11

To install all necessary package dependencies you can run:

    conda env create -f environment.yml

### Getting the environment

We have open-sourced the environment in a separate repo that you can place under the top directory by running:

    git clone https://github.com/eleninisioti/LittleAlchemy2Text.git


You can find the intro prompts for explaining the LittleAlchemy2Text tasks to the LLM agents under the prompts directory.

In particular:

* targeted_single.txt instructs a single LLM to solve a targeted task
* targeted_multi.txt instructs a group of LLMs to solve a targeted task
* openended_single.txt instructs a single LLM to solve an open-ended tasks
* openended_multi.txt instructs a group of LLMs to solve an open-ended task

### Reproducing paper results

We provide the data and visualizations used in our paper under `results/alife_2024`

### Running a new experiment

The main interface to an experiment is `play.py`. You can run an experiment by providing the appropriate flags. For example


    python play.py --agent_type llama3 --num_agents 10 --openended --num_steps 100

will create a collective of 10 agents where each one is a LLama3 model and attempt to solve an open-ended task for 100 steps.

Data and plots for each experiment are saved under a dedicated folder in directory `results`


## Cite this work

If you use this code in your work, please cite our paper:

    @article{nisioti_2024, 
    title={Collective Innovation in Groups of Large Language Models},
    author={Eleni Nisioti and Sebastian Risi and Ida Momennejad and Pierre-Yves Oudeyer and Clément Moulin-Frier},
    year={2024},
    booktitle = {The 2023 {Conference} on {Artificial} {Life}},
    publisher = {MIT Press},
    }
    

