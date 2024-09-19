# EchoMind: Audio Transcription and LLM Interaction with Ollama

## Overview

**EchoMind** is a Dockerized Python project that extracts audio from video files, transcribes the audio using OpenAI's Whisper model, and sends the transcription to the Ollama LLM for further processing based on a provided prompt. The transcription and LLM results are saved in files named after the input file.

### Key Features
- Extracts audio from video files using `ffmpeg`.
- Transcribes audio files using OpenAI's Whisper model inside the Docker container.
- Sends the transcription to the Ollama LLM API for further processing based on a provided prompt.
- Dynamically names the transcription and LLM output files based on the input filename.

## Requirements

- Docker
- A valid Ollama API URL and token.

### Building the Docker Image

First, you need to build the Docker image:

```bash
docker build -t echomind .
```

## Configuration

This project uses a `config.yml` file to store important API details like the Ollama server URL and API token. Here’s an example of the `config.yml`:

```yaml
ollama_api_url: "http://10.0.0.242:3000/ollama/api/generate"
ollama_api_token: "your-api-token-here"
model_name: "smollm:1.7b"
```

### `config.yml` parameters:
- **ollama_api_url**: The URL for the Ollama API endpoint.
- **ollama_api_token**: Your Ollama API token.
- **model_name**: The name of the model used by Ollama for processing (e.g., `smollm:1.7b`).

## How to Use

To run the project, you can pass the necessary input files (video or audio), prompt, and configuration as environment variables. The Docker container will handle the audio extraction, transcription, and LLM interaction.

### Running the Docker Container

You can run the Docker container with the following command, mapping the necessary files into the container:

```bash
docker run -it --rm \
  -v /path/to/your/local/files:/app \
  -e INPUT_FILE="file.mp4" \
  -e PROMPT_FILE="meeting.md" \
  -e CONFIG_FILE="config.yml" \
  echomind
```

This command:
- Mounts the directory containing your files to the `/app` directory inside the Docker container.
- Sets environment variables for the input file, prompt file, and config file.

### Output Files

The script will generate the following output files based on the input filename:
- **Transcription File**: `<input_filename>_transcription.txt` (e.g., `meeting_transcription.txt` for `meeting.mp4`).
- **LLM Output File**: `<input_filename>_llm_output.txt` (e.g., `meeting_llm_output.txt` for `meeting.mp4`).

### Example File Names
For an input file called `meeting.mp4`, the following files will be generated:
- `meeting_transcription.txt` (for the transcription)
- `meeting_llm_output.txt` (for the LLM output)

### Logs
The script logs its activities into a file called `echomind.log`. This log can be helpful for debugging if anything goes wrong during the process.

## Error Handling

If the script encounters an error during audio extraction, transcription, or interaction with the Ollama API, appropriate error messages will be logged, and execution will halt.

## Sample Run
This video:
https://www.youtube.com/watch?v=lBVtvOpU80Q

To strip the mp3 out (ffmpeg):
About 5 to 7 seconds

Speech to text (whisper):
4 minutes

Call to ollama (open-web-ui/completions api) (nvidia 4000, 8GB):
About 1 minute

Model:mistral-small:22b

Prompt:
https://github.com/nothingmn/echomind/blob/main/meeting.md
(needs work for sure)
Mostly borrowed from fabric
https://github.com/danielmiessler/fabric/blob/main/patterns/transcribe_minutes/system.md

[Transcription](sample_output/meeting_llm_output.txt)
[Model output](sample_output/meeting_transcription.txt)



## License

This project is open source under the MIT License.

---
