# Use the official Python image from Docker Hub (latest Python version)
FROM python:3.11-slim

# Install ffmpeg and other necessary dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Install necessary Python packages (whisper, pyyaml, requests, ollama)
RUN pip install --upgrade pip && \
    pip install git+https://github.com/openai/whisper.git pyyaml requests && \
    pip install git+https://github.com/ollama/ollama-python.git

# Copy the Python scripts and configuration files into the container
COPY . .

# Set the default command to run your main Python script
CMD ["python", "transcribe_and_ollama.py"]
