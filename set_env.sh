#!/bin/bash
set -e

# Customize this if needed
ENV_NAME="CCMU"

# Step 1: Create conda environment
echo "Creating conda environment from environment.yml..."
conda env create -f environment.yml -n "$ENV_NAME"

# Step 2: Activate the environment
echo "Activating environment: $ENV_NAME"
# For script context
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

# Step 3: Install pip requirements (if file exists and is non-empty)
if [[ -s requirements.txt ]]; then
    echo "Installing pip packages from requirements.txt..."
    pip install -r requirements.txt
else
    echo "No valid requirements.txt found or it's empty. Skipping pip install."
fi

echo "Environment '$ENV_NAME' setup complete."
