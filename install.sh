#!/bin/bash

ENV_NAME="replicant_fishing_bot"

# Check for conda
if ! command -v conda &> /dev/null; then
    echo "Error: Conda is not installed or not in PATH."
    echo "Please install Miniconda or Anaconda first."
    exit 1
fi

# Check if env exists
if conda env list | grep -q "$ENV_NAME"; then
    echo "Conda environment '$ENV_NAME' already exists."
else
    echo "Creating Conda environment '$ENV_NAME'..."
    conda create -y -n "$ENV_NAME" python=3.11
fi

# Activate the environment
echo "Activating environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "No requirements.txt found. Skipping pip install."
fi

echo ""
echo "Done! To activate later, run:"
echo "  conda activate $ENV_NAME"
