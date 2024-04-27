# CollectiveLLM

This is the code accompanying our submission to ALife 2024 "Collective innovation with Large Language Models."

You can find the intro prompts for explaining the task to the LLM agents under the prompts directory.

In particular:

* targeted_single.txt instructs a single LLM to solve a targeted task
* targeted_multi.txt instructs a group of LLMs to solve a targeted task
* openended_single.txt instructs a single LLM to solve an open-ended tasks
* openended_multi.txt instructs a group of LLMs to solve an open-ended task
* test_knowledge.txt is the prompt for the prob that tests whether the LLM can predict the outcome of combinations

Under scripts you can find scripts for running our experiments and reproducing the visualisations in the paper

The main interface to an experiment is structured_multi_LLM/play.py. 
By providing the appropriate flags you can run single-agent or multi-agent groups,
targeted or open-ended tasks


