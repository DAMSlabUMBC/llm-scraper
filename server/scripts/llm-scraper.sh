#!/bin/bash
#SBATCH --cluster=chip-gpu
#SBATCH --account=pi_ryus
#SBATCH --partition=gpu
#SBATCH --job-name=llm-scraper              # Job name to appear in the SLURM queue
#SBATCH --mail-user=gsantos2@umbc.edu       # Email for job notifications (replace with your email)
#SBATCH --mail-type=END,FAIL                # Notify on job completion or failure
#SBATCH --mem=150000                        # Memory allocation in MB (150 GB)
#SBATCH --time=72:00:00                     # Maximum runtime for the job (70 hours)
#SBATCH --constraint=L40S               # Specific hardware constraint
#SBATCH --gres=gpu:1                        # Request 4 GPU for the job
#SBATCH --output=llm-scraper_output/llm-scraper_%A_%a.out       # Output log (include %A for job ID, %a for array index)
#SBATCH --error=llm-scraper_error/llm-scraper_%A_%a.err        # Error log

Notify user the job has started
echo "SLURM job started at $(date)"
echo "Running Ollama batch script..."

module load ollama/0.6.5
echo "loaded all necessary modules"
#install dependencies if needed (comment out if pre-installed)
#pip install --user pandas tqdm ollama

# initializes conda environment
#conda init bash

# activate conda environment
conda init
source ~/.bashrc
conda activate test_env2

conda list

sleep 10 # Wait 10 seconds to ensure conda environment has been activated

Set up Ollama-specific environment variables
export OLLAMA_TMPDIR=/umbc/ada/ryus/users/gsantos2/ollama/ollama_tmp # Temporary directory for Ollama
export OLLAMA_HOST="0.0.0.0" # Host address for Ollama server

Start the Ollama server in the background
echo "Starting Ollama server..."
ollama serve &

Allow time for the Ollama server to initialize
sleep 10 # Wait 10 seconds to ensure the server is ready

Pull the required models to ensure they are cached locally
echo "Pulling required models for Ollama..."
ollama pull deepseek-r1:70b
ollama pull llava:34b

echo "validating pulled ollama models"
ollama list

Notify that model pulling is complete
echo "Model pulling complete. Starting Python script execution..."

sleep 15

# Changing Python path to have the correct version
# echo 'export PATH=/home/gsantos2/.conda/envs/test_env2/bin:$PATH' >> ~/.bashrc
# source ~/.bashrc

Checking Python version
python --version

Run the Python script with input, combination, and output file paths
#python main.py --input_file=Amazon_product_urls.txt --output_file=output.txt
python main.py --config_file="best_buy_config.json"

Notify that the Python script execution has finished
echo "Python script execution completed."

Stop the Ollama server to free resources
pkill -f "ollama serve"

Notify that the job has completed
echo "SLURM job completed at $(date)"
echo "Logs saved to batch_output.out (standard output) and batch_error.err (error log)"