#!/bin/bash
 
 docker build -t echomind .

# Check if correct number of arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: ./run_echomind.sh <input_file> <prompt_file> <config_file>"
    exit 1
fi

# Assign input arguments to variables
INPUT_FILE=$1
PROMPT_FILE=$2
CONFIG_FILE=$3

# Run the Docker command with the provided arguments
docker run -it --rm \
  -v "$(pwd):/app" \
  -e INPUT_FILE="$INPUT_FILE" \
  -e PROMPT_FILE="$PROMPT_FILE" \
  -e CONFIG_FILE="$CONFIG_FILE" \
  echomind
