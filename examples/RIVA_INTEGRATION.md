# NVIDIA Riva Integration Setup Guide

## Overview

This guide covers the setup and integration of NVIDIA Riva speech services with your self-hosted AI starter kit. NVIDIA Riva provides state-of-the-art speech AI capabilities including:

- **Automatic Speech Recognition (ASR)** - Convert speech to text
- **Text-to-Speech (TTS)** - Convert text to natural speech  
- **Natural Language Processing (NLP)** - Intent recognition, entity extraction, etc.

## Prerequisites

### 1. NVIDIA Riva Dependencies
```bash
# Install NVIDIA Riva Python client
pip install nvidia-riva-client

# Install audio processing dependencies
pip install soundfile librosa websockets

# Install FastAPI file upload support
pip install python-multipart
```

### 2. NVIDIA Riva Server Setup

You have two options for running NVIDIA Riva:

#### Option A: Local NVIDIA Riva Server
1. Follow the [NVIDIA Riva Quick Start Guide](https://docs.nvidia.com/deeplearning/riva/user-guide/docs/quick-start-guide.html)
2. Download and start the Riva server locally
3. Default server runs on `localhost:50051`

#### Option B: NVIDIA Cloud Services (Recommended)
1. Get an NVIDIA API key from the [NVIDIA Developer Portal](https://developer.nvidia.com/)
2. Set the API key in your environment variables

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# NVIDIA Riva Configuration
NVIDIA_RIVA_API_KEY=nvapi-your-api-key-here  # For cloud services
RIVA_SERVER=localhost:50051                   # For local server
RIVA_API_PORT=8001                           # Port for our Riva API server
```

### Docker Compose Integration

The Riva service is already configured in `docker-compose.yml`:

```yaml
services:
  riva:
    image: nvcr.io/nvidia/riva/riva-speech:2.14.0
    environment:
      - NVIDIA_RIVA_API_KEY=${NVIDIA_RIVA_API_KEY}
    # ... other configuration
```

## Usage

### Starting the Riva API Server

```bash
# Activate the conda environment
conda activate ai-starter-kit

# Start the Riva API server
python examples/riva_api_server.py
```

The server will start on `http://localhost:8001` with the following endpoints:

- `GET /health` - Health check
- `GET /riva-status` - Detailed Riva service status
- `POST /speech-to-text` - Convert audio to text
- `POST /text-to-speech` - Convert text to audio
- `GET /docs` - Interactive API documentation

### API Examples

#### Text-to-Speech
```bash
curl -X POST "http://localhost:8001/text-to-speech" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from NVIDIA Riva!","voice":"English-US.Female-1"}' \
  --output speech.wav
```

#### Speech-to-Text
```bash
curl -X POST "http://localhost:8001/speech-to-text" \
  -F "audio_file=@/path/to/audio.wav" \
  -F "language_code=en-US"
```

### Python Integration Examples

#### Using the Riva Client Directly
```python
from examples.riva_integration_example import RivaClient

# Initialize client
client = RivaClient(
    server="localhost:50051",  # or use cloud services
    api_key="your-api-key"     # for cloud services
)

# Text-to-Speech
audio_data = client.synthesize_speech("Hello, world!")

# Speech-to-Text  
transcript = client.transcribe_audio("audio_file.wav")

# NLP - Intent Analysis
intent_result = client.analyze_intent("What's the weather like?")
```

#### Using the API Server
```python
import requests

# Text-to-Speech via API
response = requests.post("http://localhost:8001/text-to-speech", 
    json={"text": "Hello from our AI system!", "voice": "English-US.Female-1"})

with open("output.wav", "wb") as f:
    f.write(response.content)

# Speech-to-Text via API
with open("input.wav", "rb") as f:
    files = {"audio_file": f}
    data = {"language_code": "en-US"}
    response = requests.post("http://localhost:8001/speech-to-text", 
                           files=files, data=data)
    
transcript = response.json()["transcription"]
```

### n8n Integration

#### Using HTTP Request Nodes

1. **Text-to-Speech in n8n:**
   - Add an HTTP Request node
   - Method: POST
   - URL: `http://localhost:8001/text-to-speech`
   - Body Type: JSON
   - Body: `{"text": "{{ $json.text_to_speak }}", "voice": "English-US.Female-1"}`

2. **Speech-to-Text in n8n:**
   - Add an HTTP Request node  
   - Method: POST
   - URL: `http://localhost:8001/speech-to-text`
   - Body Type: Form Data
   - Add fields: `audio_file` (file), `language_code` (text)

#### Workflow Examples

- **Voice Assistant:** ASR → NLP → Business Logic → TTS
- **Audio Transcription:** File Upload → ASR → Text Processing → Save
- **Voice Notifications:** Event Trigger → Generate Message → TTS → Audio Output

## Troubleshooting

### Common Issues

#### 1. Riva Service Not Available
```bash
# Check Riva status
curl http://localhost:8001/riva-status

# Verify environment variables
echo $NVIDIA_RIVA_API_KEY
echo $RIVA_SERVER
```

#### 2. Audio Format Issues
- Ensure audio files are in supported formats (WAV, MP3, FLAC)
- Check sample rates (16kHz recommended for ASR)
- Verify file size limits

#### 3. Authentication Errors
- Verify API key is correctly set
- Check that the key has appropriate permissions
- For local servers, ensure no authentication is required

#### 4. Import Errors
```bash
# Verify Riva client installation
python -c "import riva.client; print('✓ Riva client available')"

# Check audio libraries
python -c "import soundfile, librosa; print('✓ Audio libraries available')"
```

### Debug Mode

Enable debug logging in the Riva API server:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Optimization

- **Batch Processing:** Use streaming APIs for real-time applications
- **Caching:** Cache frequently used audio synthesis results
- **Model Selection:** Choose appropriate voice models for your use case
- **Hardware:** Use GPU acceleration when available

## Advanced Features

### Custom Voice Models
- Train custom voice models using NVIDIA NeMo
- Deploy custom models to Riva server
- Use custom voices in synthesis requests

### Streaming APIs
- Real-time speech recognition
- Streaming text-to-speech synthesis  
- Low-latency applications

### Multi-language Support
- Configure multiple language models
- Dynamic language detection
- Language-specific voice selection

## Security Considerations

### API Keys
- Store API keys securely in environment variables
- Rotate keys regularly
- Use minimal permissions

### Network Security
- Use HTTPS in production
- Implement rate limiting
- Add authentication to your API endpoints

### Data Privacy
- Audio data handling policies
- Temporary file cleanup
- Compliance with privacy regulations

## Production Deployment

### Scaling
- Load balancing multiple Riva instances
- Horizontal scaling with container orchestration
- Monitoring and alerting

### Monitoring
- Track API response times
- Monitor resource usage
- Set up health checks

### Backup and Recovery
- Model file backups
- Configuration management
- Disaster recovery procedures

## Resources

- [NVIDIA Riva Documentation](https://docs.nvidia.com/deeplearning/riva/user-guide/docs/)
- [Python Client Repository](https://github.com/nvidia-riva/python-clients)
- [NeMo Toolkit](https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/)
- [NVIDIA Developer Portal](https://developer.nvidia.com/)
