#!/bin/bash

#SBATCH --job-name=llm-scraper              # Job name to appear in the SLURM queue
#SBATCH --array=2-31                        # Run array tasks 0..999 (i.e. 1000 tasks)
#SBATCH --mail-user=gsantos2@umbc.edu       # Email for job notifications (replace with your email)
#SBATCH --mail-type=END,FAIL                # Notify on job completion or failure
#SBATCH --mem=150000                        # Memory allocation in MB (150 GB)
#SBATCH --time=72:00:00                     # Maximum runtime for the job (70 hours)
#SBATCH --constraint=rtx_8000               # Specific hardware constraint
#SBATCH --gres=gpu:1                        # Request 4 GPU for the job
#SBATCH --output=llm-scraper_output/llm-scraper_%A_%a.out       # Output log (include %A for job ID, %a for array index)
#SBATCH --error=llm-scraper_error/llm-scraper_%A_%a.err        # Error log

echo "SLURM job started at $(date)"
echo "Array Task ID: $SLURM_ARRAY_TASK_ID"

# load necessary modules
module load ollama

# (Optional) pip install commands
#pip install --user pandas tqdm ollama

# activate conda environment
conda activate test_env2

sleep 10 # Wait 10 seconds to ensure conda environment has been activated

# Set a unique port for this array task
PORT="$((11434 + SLURM_ARRAY_TASK_ID))"
export PORT
echo "Starting Ollama server on port ${PORT}..."

export OLLAMA_TMPDIR=/nfs/ada/ryus/users/gsantos2/ollama/ollama_tmp # Temporary directory for Ollama
export OLLAMA_HOST="0.0.0.0:"
OLLAMA_HOST+="${PORT}"
echo "PORT=${PORT}"
echo "OLLAMA_HOST=${OLLAMA_HOST}"

echo $OLLAMA_HOST

# Start *this task's* Ollama server in the background, on a unique port
# OLLAMA_TMPDIR=/nfs/ada/ryus/users/sbelon1/ollama_temp/ArrOll \  #this should be the path to your soft link
# OLLAMA_HOST="0.0.0.0:$(PORT)" \
ollama serve &

# Wait a bit for it to come up
sleep 10

# (Optional) Pre-pull required models
ollama pull deepseek-r1:70b
ollama pull llava:34b

echo "Model pulling complete. Starting Python script execution..."

# Changing Python path to have the correct version
echo 'export PATH=/home/gsantos2/.conda/envs/test_env2/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Checking Python version
python --version

#CHUNK_SIZE=1

# Wait a bit before running python script
sleep 10

# Use python to run queries
python main.py \
  --input_folder="amazon_batches/batch_${SLURM_ARRAY_TASK_ID}" \
  --output_file="amazon_triplets/triplets_${SLURM_ARRAY_TASK_ID}" \
  --ollama_port="${PORT}"

echo "Python script done for task ${SLURM_ARRAY_TASK_ID}."

# Optional: kill only this task's Ollama server by port, rather than pkill
# so we don't kill other tasks' servers running on different ports
# echo "Terminating Ollama server on port ${PORT}..."
# lsof -ti tcp:${PORT} | xargs -r kill -9

echo "SLURM job completed at $(date)"
