#!/bin/bash

ENV_DIR="venv"

# Create venv if it doesn't exist
if [ ! -d "$ENV_DIR" ]; then
    echo "Creating virtual environment in $ENV_DIR..."
    python3 -m venv "$ENV_DIR"
else
    echo "Virtual environment '$ENV_DIR' already exists."
fi

# Activate the virtual environment
source "$ENV_DIR/bin/activate"

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "No requirements.txt file found."
fi

echo ""
echo "Done! To activate the environment manually later, run:"
echo "  source $ENV_DIR/bin/activate"
