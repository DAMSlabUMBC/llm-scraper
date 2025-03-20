#!/bin/bash
#SBATCH --job-name=llm_scraper # Job name to appear in the SLURM queue
#SBATCH --mail-user=gsantos2@umbc.edu # Email for job notifications (replace with your email)
#SBATCH --mail-type=END,FAIL # Notify on job completion or failure
#SBATCH --mem=150000 # Memory allocation in MB (40 GB)
#SBATCH --time=72:00:00 # Maximum runtime for the job (70 hours)
#SBATCH --constraint=rtx_8000 # Specific hardware constraint
#SBATCH --gres=gpu:1 # Request 4 GPU for the job
#SBATCH --output=batch_output_tr0.out # Standard output log file
#SBATCH --error=batch_error_tr0.err # Standard error log file

Notify user the job has started
echo "SLURM job started at $(date)"
echo "Running Ollama batch script..."

Load the necessary modules
#module load Python/3.9.6-GCCcore-11.2.0 # Load the Python module
module load ollama # Load the Ollama module for querying models

#install dependencies if needed (comment out if pre-installed)
#pip install --user pandas tqdm ollama

# initializes conda environment
#conda init bash

# activate conda environment
conda activate test_env2

sleep 10 # Wait 10 seconds to ensure conda environment has been activated

# checking current conda environments
conda info --envs

Set up Ollama-specific environment variables
export OLLAMA_TMPDIR=/nfs/ada/ryus/users/gsantos2/ollama/ollama_tmp # Temporary directory for Ollama
export OLLAMA_HOST="0.0.0.0" # Host address for Ollama server

Start the Ollama server in the background
echo "Starting Ollama server..."
OLLAMA_TMPDIR=/nfs/ada/ryus/users/gsantos2/ollama/ollama_tmp ollama serve &

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

Changing Python path to have the correct version
echo 'export PATH=/home/gsantos2/.conda/envs/test_env2/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

Checking Python version
python --version

Run the Python script with input, combination, and output file paths
#python main.py --input_file=Amazon_product_urls.txt --output_file=output.txt
python main.py --input_folder="amazon_batches/batch_1" --output_file="amazon_triplets/triplets_1"

Notify that the Python script execution has finished
echo "Python script execution completed."

Stop the Ollama server to free resources
pkill -f "ollama serve"

Notify that the job has completed
echo "SLURM job completed at $(date)"
echo "Logs saved to batch_output.out (standard output) and batch_error.err (error log)"