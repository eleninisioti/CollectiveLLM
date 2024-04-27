#!/bin/bash
#SBATCH --job-name=/knowledge_llama
#SBATCH -A imi@v100
#SBATCH --gres=gpu:2
#SBATCH --cpus-per-task=13
#SBATCH --time=05:00:00
#SBATCH --hint=nomultithread
#SBATCH --partition=gpu_p2l
#SBATCH --output=/gpfsscratch/rech/imi/utw61ti/multiLLM_log/jz_logs/knowledge_llama%j.out
#SBATCH --error=/gpfsscratch/rech/imi/utw61ti/multiLLM_log/jz_logs/knowledge_llama%j.err
source ~/.bashrc
conda activate llm
torchrun --nproc_per_node 2 scripts/papers/alife/run.py