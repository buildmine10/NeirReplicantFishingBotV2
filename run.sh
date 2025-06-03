#!/bin/bash

CONDA_ENV="replicant_fishing_bot"
VENV_DIR="venv"
SCRIPT="NeiRReplicantFishingBot.py"

# Check for conda
if command -v conda &> /dev/null; then
    # Check if conda env exists
    if conda env list | grep -q "$CONDA_ENV"; then
        echo "Activating Conda environment: $CONDA_ENV"
        source "$(conda info --base)/etc/profile.d/conda.sh"
        conda activate "$CONDA_ENV"
        python "$SCRIPT"
        exit 0
    else
        echo "Conda is installed, but environment '$CONDA_ENV' not found."
    fi
else
    echo "Conda is not installed or not in PATH."
fi

# Fall back to venv
if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "Activating Python virtual environment: $VENV_DIR"
    source "$VENV_DIR/bin/activate"
    python "$SCRIPT"
    exit 0
else
    echo "No Python virtual environment found."
    echo "Please run install_env_python.sh first."
    exit 1
fi
