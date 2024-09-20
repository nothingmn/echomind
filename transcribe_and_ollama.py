import os
import subprocess
import whisper
import yaml
import logging
import requests
import json
from datetime import datetime
import warnings

# Suppress FutureWarnings and UserWarnings reduce the noise
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("echomind.log"),
        logging.StreamHandler()  # This will print to stdout (console)
    ]
)

# Step 1: Load config.yml for Ollama API details
def load_config(config_file):
    logging.debug(f"Loading config from {config_file}")
    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
            logging.debug(f"Config loaded successfully: {config}")
            return config
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        raise

# Step 2: Extract audio using ffmpeg (only if input is a video file)
def extract_audio(video_file, audio_file):
    logging.debug(f"Extracting audio from video file: {video_file}")
    try:
        command = f"ffmpeg -i {video_file} -q:a 0 -map a {audio_file} -y"
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.info(f"Audio extracted to {audio_file}")
        logging.debug(f"ffmpeg output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to extract audio: {e.stderr}")
        raise

# Step 3: Transcribe audio using Whisper, with optional model size
def transcribe_audio(audio_file, transcription_file, whisper_model="base"):
    logging.debug(f"Transcribing audio from file: {audio_file} using model: {whisper_model}")
    try:
        model = whisper.load_model(whisper_model)  # Load the specified Whisper model
        logging.debug(f"Whisper model '{whisper_model}' loaded successfully")
        result = model.transcribe(audio_file)
        logging.info(f"Transcription completed. Saving to {transcription_file}")
        with open(transcription_file, 'w') as f:
            f.write(result['text'])
        logging.debug(f"Transcription saved: {result['text'][:100]}...")  # Log first 100 characters
        return result['text']
    except Exception as e:
        logging.error(f"Failed to transcribe audio: {e}")
        raise

# Step 4: Send transcription and prompt to Ollama LLM using the requests library
def send_to_ollama(model_name, prompt_file, transcription, ollama_api_url, ollama_api_token):
    logging.debug(f"Preparing request to Ollama LLM using the '{model_name}' model at '{ollama_api_url}', token is: '{ollama_api_token}'")
    
    try:
        # Read the prompt from the provided file
        with open(prompt_file, 'r') as file:
            prompt = file.read()
        logging.debug(f"Prompt loaded: {prompt[:100]}...")  # Log first 100 characters

        # Combine the prompt and transcription
        combined_prompt = prompt + "\n\n" + transcription

        # Set up the headers
        headers = {
            "Authorization": f"Bearer {ollama_api_token}",
            "Content-Type": "application/json"
        }

        # Create the payload (data) for the request
        data = {
            "model": model_name,
            "prompt": combined_prompt,
            "stream": False
        }

        # Perform the POST request to the Ollama server
        response = requests.post(ollama_api_url, headers=headers, data=json.dumps(data))

        # Check for errors in the response
        if response.status_code == 200:
            logging.info(f"Received response from Ollama: {response.json()}")
            return response.json().get('response', 'No text found in response')
        else:
            logging.error(f"Failed to send request to Ollama LLM: {response.status_code} - {response.text}")
            raise Exception(f"Request failed: {response.status_code} - {response.text}")

    except Exception as e:
        logging.error(f"Failed to send request to Ollama LLM: {e}")
        raise

# Helper function: Determine if the file is video or audio based on MIME type
def is_video_file(file_path):
    logging.debug(f"Checking if {file_path} is a video file")
    import mimetypes
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and mime_type.startswith('video'):
        logging.debug(f"{file_path} is a video file")
        return True
    else:
        logging.debug(f"{file_path} is not a video file")
        return False

# Step 5: Main function to handle everything
def main(input_file, prompt_file, config_file, whisper_model=None):
    logging.info(f"Starting processing for {input_file} {prompt_file} {config_file}")

    # Step 1: Load config
    config = load_config(config_file)

    # Get the base filename without the extension
    base_filename = os.path.splitext(os.path.basename(input_file))[0]

    # Define file names based on the input filename
    audio_file = f"{base_filename}_audio.mp3"
    transcription_file = f"{base_filename}_transcription.txt"
    output_file = f"{base_filename}_llm_output.txt"
    model_name = config.get('model_name', 'smollm:1.7b')  # Example model, replace with correct one

    ollama_api_token = config.get('ollama_api_token')
    ollama_api_url = config.get('ollama_api_url')

    # Get whisper model from config or override via CLI
    whisper_model = whisper_model or config.get('whisper_model', 'base')  # Default to "base"

    # Step 2: Determine if input file is a video or audio file
    if is_video_file(input_file):
        logging.info(f"{input_file} is a video file. Extracting audio...")
        extract_audio(input_file, audio_file)  # Extract audio from video
    else:
        logging.info(f"{input_file} is an audio file. Skipping audio extraction...")
        audio_file = input_file  # Use the audio file directly

    # Step 3: Transcribe audio with the specified Whisper model
    transcription = transcribe_audio(audio_file, transcription_file, whisper_model)

    # Step 4: Send transcription and prompt to Ollama LLM
    llm_output = send_to_ollama(model_name, prompt_file, transcription, ollama_api_url, ollama_api_token)

    # Step 5: Save LLM output to a file
    try:
        with open(output_file, 'w') as f:
            f.write(llm_output)
        logging.info(f"LLM output saved to {output_file}")
    except Exception as e:
        logging.error(f"Failed to save LLM output: {e}")
        raise

if __name__ == "__main__":
    import sys
    
    # Check for environment variables first, then fallback to command-line arguments
    input_file = os.getenv("INPUT_FILE", sys.argv[1] if len(sys.argv) > 1 else "file.mp4")
    prompt_file = os.getenv("PROMPT_FILE", sys.argv[2] if len(sys.argv) > 2 else "prompt.txt")
    config_file = os.getenv("CONFIG_FILE", sys.argv[3] if len(sys.argv) > 3 else "config.yml")
    whisper_model = os.getenv("WHISPER_MODEL", sys.argv[4] if len(sys.argv) > 4 else None)  # Can override via CLI

    main(input_file, prompt_file, config_file, whisper_model)
