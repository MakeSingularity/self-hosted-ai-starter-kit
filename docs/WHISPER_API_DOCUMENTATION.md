# Whisper Speech Recognition API Documentation

## Overview

The Whisper Speech Recognition API provides local, free speech-to-text transcription using Ollama's Whisper models. It's specifically designed for integration with n8n workflows handling Telegram voice messages.

## Features

- ✅ Local Whisper models via Ollama (no external API costs)
- ✅ FastAPI-based REST endpoints
- ✅ Telegram message format support
- ✅ n8n workflow integration ready
- ✅ Automatic model fallback (large → tiny)
- ✅ Comprehensive error handling
- ✅ Audio format conversion support

## Available Models

- **Primary**: `ZimaBlueAI/whisper-large-v3:latest` (849.7 MB) - High accuracy
- **Fallback**: `dimavz/whisper-tiny:latest` (42.0 MB) - Fast processing

## API Endpoints

### Health Check
```
GET /
```
Returns basic API status and readiness information.

### Detailed Status
```
GET /status
```
Returns comprehensive status including:
- Ollama connection status
- Available Whisper models
- Configuration details

### n8n Integration (Primary Endpoint)
```
POST /transcribe/n8n
```
Optimized for n8n Telegram workflows. Handles:
- Voice messages
- Audio messages  
- Text messages (pass-through)

**Request Format:**
```json
{
  "message": {
    "voice": {
      "file_id": "telegram_file_id",
      "duration": 5
    },
    "from": {
      "id": 123456789,
      "username": "user"
    }
  }
}
```

**Response Format:**
```json
{
  "success": true,
  "message_type": "voice",
  "transcription": {
    "text": "Transcribed text here",
    "confidence": 0.95,
    "language": "en",
    "duration": 5,
    "model_used": "ZimaBlueAI/whisper-large-v3:latest"
  },
  "needs_transcription": true,
  "original_message": {...}
}
```

### File Upload Transcription
```
POST /transcribe/file
```
Upload audio files directly for transcription.

### Model Testing
```
GET /test/models
```
Test availability and status of all Whisper models.

### Local File Testing
```
POST /test/local
```
Test transcription with local file paths (development only).

## Installation & Setup

### 1. Install Dependencies
```bash
pip install fastapi uvicorn[standard] python-multipart
```

### 2. Start the Server
```bash
# Development mode (with auto-reload)
python scripts/whisper_api_simple.py

# Production mode (stable)
python scripts/start_whisper_api.py
```

### 3. Optional: Set Telegram Bot Token
```bash
# For full Telegram integration
set TELEGRAM_BOT_TOKEN=your_bot_token_here
```

## n8n Workflow Integration

### Step 1: Add HTTP Request Node
- **Method**: POST
- **URL**: `http://localhost:8000/transcribe/n8n`
- **Headers**: `Content-Type: application/json`
- **Body**: Pass the entire Telegram message object

### Step 2: Add Conditional Logic
```javascript
// Check if transcription is needed
{{ $json.needs_transcription ? $json.transcription.text : $json.original_message.text }}
```

### Step 3: Handle Voice vs Text Messages
```javascript
// Route based on message type
if ($json.message_type === "voice" || $json.message_type === "audio") {
  // Use transcribed text
  return $json.transcription.text;
} else {
  // Use original text
  return $json.original_message.text;
}
```

## Testing

Run the comprehensive test suite:
```bash
python scripts/test_whisper_api.py
```

This tests:
- API health and connectivity
- Whisper model availability
- n8n endpoint functionality
- Text message handling
- Error conditions

## Performance Notes

- **Large Model**: Higher accuracy, ~2-3 seconds processing time
- **Tiny Model**: Lower accuracy, ~0.5-1 second processing time
- **Automatic Fallback**: If large model fails, automatically tries tiny model
- **Local Processing**: No external API calls or data sharing

## Error Handling

The API includes comprehensive error handling:
- Model unavailability
- Audio format issues
- Network connectivity problems
- Invalid request formats

All errors return structured JSON responses with detailed error information.

## Production Deployment

### Docker Integration (Future)
```dockerfile
# Add to your existing docker-compose.yml
whisper-api:
  build: ./scripts
  ports:
    - "8000:8000"
  depends_on:
    - ollama
  networks:
    - ai-network
```

### Environment Variables
- `TELEGRAM_BOT_TOKEN`: For Telegram file downloads
- `OLLAMA_URL`: Custom Ollama endpoint (default: http://localhost:11434)
- `LOG_LEVEL`: Logging verbosity (default: info)

## Security Considerations

- API runs on localhost by default
- No external API keys required
- All processing is local
- No audio data sent to external services

## Troubleshooting

### Common Issues

1. **"No module named 'fastapi'"**
   ```bash
   pip install fastapi uvicorn[standard]
   ```

2. **"Could not connect to Ollama"**
   - Ensure Ollama is running: `docker ps`
   - Check Ollama models: `docker exec ollama ollama list`

3. **"Whisper models not found"**
   ```bash
   docker exec ollama ollama pull ZimaBlueAI/whisper-large-v3:latest
   docker exec ollama ollama pull dimavz/whisper-tiny:latest
   ```

4. **"Telegram bot token not configured"**
   - Set environment variable: `set TELEGRAM_BOT_TOKEN=your_token`
   - Or run without token for local file testing only

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## API Documentation

Once running, visit:
- **Interactive docs**: http://localhost:8000/docs
- **API spec**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
