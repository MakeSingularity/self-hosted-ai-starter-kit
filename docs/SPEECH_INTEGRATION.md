# NVIDIA Riva Speech Services Integration with n8n

This document provides a complete guide for integrating speech services (Text-to-Speech and Speech-to-Text) with your n8n workflows using the self-hosted AI starter kit.

## Overview

The hybrid speech API server provides multiple TTS and ASR engines:
- **NVIDIA Riva** (Cloud/Local): High-quality enterprise speech services
- **pyttsx3** (Local): Reliable fallback TTS engine
- **Edge TTS** (Cloud): Microsoft's text-to-speech service

## Quick Start

### 1. Verify Speech Services

First, ensure the speech API server is running:

```bash
# Check if the server is running
curl http://localhost:8001/health

# Expected response:
{
  "status": "healthy",
  "engines": {
    "riva": true,
    "pyttsx3": true,
    "edge_tts": false
  },
  "primary_engine": "riva"
}
```

### 2. Available Endpoints

#### Health Check
- **URL**: `GET http://localhost:8001/health`
- **Description**: Check if services are available

#### List Engines
- **URL**: `GET http://localhost:8001/engines`
- **Description**: See all available TTS and ASR engines

#### Text-to-Speech
- **URL**: `POST http://localhost:8001/text-to-speech`
- **Content-Type**: `application/json`
- **Body**:
```json
{
  "text": "Hello, this is a test message",
  "voice": "English-US.Female-1",
  "engine": "auto"
}
```

#### Speech-to-Text
- **URL**: `POST http://localhost:8001/speech-to-text`
- **Content-Type**: `multipart/form-data`
- **Body**: Audio file + optional engine parameter

## n8n Integration Examples

### Example 1: Simple Text-to-Speech Workflow

```json
{
  "name": "Text to Speech",
  "nodes": [
    {
      "name": "Trigger",
      "type": "n8n-nodes-base.manualTrigger",
      "position": [240, 300],
      "parameters": {}
    },
    {
      "name": "Set Text",
      "type": "n8n-nodes-base.set",
      "position": [460, 300],
      "parameters": {
        "values": {
          "string": [
            {
              "name": "message",
              "value": "Welcome to the AI-powered workflow! This message will be converted to speech."
            }
          ]
        }
      }
    },
    {
      "name": "Convert to Speech",
      "type": "n8n-nodes-base.httpRequest",
      "position": [680, 300],
      "parameters": {
        "url": "http://localhost:8001/text-to-speech",
        "method": "POST",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "text",
              "value": "={{$node['Set Text'].json['message']}}"
            },
            {
              "name": "voice",
              "value": "English-US.Female-1"
            },
            {
              "name": "engine",
              "value": "auto"
            }
          ]
        },
        "options": {
          "response": {
            "response": {
              "responseFormat": "file"
            }
          }
        }
      }
    },
    {
      "name": "Save Audio File",
      "type": "n8n-nodes-base.writeFile",
      "position": [900, 300],
      "parameters": {
        "fileName": "speech_output.wav",
        "data": "={{$node['Convert to Speech'].binary}}"
      }
    }
  ],
  "connections": {
    "Trigger": {
      "main": [
        [
          {
            "node": "Set Text",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Set Text": {
      "main": [
        [
          {
            "node": "Convert to Speech",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Convert to Speech": {
      "main": [
        [
          {
            "node": "Save Audio File",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### Example 2: Speech-to-Text with File Processing

```json
{
  "name": "Speech to Text",
  "nodes": [
    {
      "name": "Watch Audio Folder",
      "type": "n8n-nodes-base.localFileTrigger",
      "position": [240, 300],
      "parameters": {
        "path": "/shared/audio_input/",
        "watchOptions": {}
      }
    },
    {
      "name": "Transcribe Audio",
      "type": "n8n-nodes-base.httpRequest",
      "position": [460, 300],
      "parameters": {
        "url": "http://localhost:8001/speech-to-text",
        "method": "POST",
        "sendQuery": false,
        "sendHeaders": false,
        "sendBody": true,
        "bodyParametersUi": {
          "parameter": [
            {
              "name": "audio",
              "value": "={{$node['Watch Audio Folder'].binary.data}}"
            },
            {
              "name": "engine",
              "value": "auto"
            }
          ]
        },
        "options": {
          "bodyContentType": "multipart-form-data"
        }
      }
    },
    {
      "name": "Process Transcript",
      "type": "n8n-nodes-base.set",
      "position": [680, 300],
      "parameters": {
        "values": {
          "string": [
            {
              "name": "transcript",
              "value": "={{$node['Transcribe Audio'].json['transcript']}}"
            },
            {
              "name": "confidence",
              "value": "={{$node['Transcribe Audio'].json['confidence']}}"
            },
            {
              "name": "engine_used",
              "value": "={{$node['Transcribe Audio'].json['engine_used']}}"
            }
          ]
        }
      }
    }
  ]
}
```

### Example 3: Voice-Interactive AI Assistant

```json
{
  "name": "Voice AI Assistant",
  "nodes": [
    {
      "name": "Voice Input Trigger",
      "type": "n8n-nodes-base.webhook",
      "position": [240, 300],
      "parameters": {
        "path": "voice-input",
        "responseMode": "responseNode"
      }
    },
    {
      "name": "Transcribe Voice",
      "type": "n8n-nodes-base.httpRequest",
      "position": [460, 300],
      "parameters": {
        "url": "http://localhost:8001/speech-to-text",
        "method": "POST",
        "sendBody": true,
        "bodyParametersUi": {
          "parameter": [
            {
              "name": "audio",
              "value": "={{$node['Voice Input Trigger'].binary.data}}"
            }
          ]
        },
        "options": {
          "bodyContentType": "multipart-form-data"
        }
      }
    },
    {
      "name": "Query AI Model",
      "type": "n8n-nodes-base.httpRequest",
      "position": [680, 300],
      "parameters": {
        "url": "http://localhost:8000/v1/chat/completions",
        "method": "POST",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "model",
              "value": "llama3.2"
            },
            {
              "name": "messages",
              "value": "=[{\"role\": \"user\", \"content\": \"{{$node['Transcribe Voice'].json['transcript']}}\"}]"
            },
            {
              "name": "max_tokens",
              "value": 150
            }
          ]
        }
      }
    },
    {
      "name": "Convert Response to Speech",
      "type": "n8n-nodes-base.httpRequest",
      "position": [900, 300],
      "parameters": {
        "url": "http://localhost:8001/text-to-speech",
        "method": "POST",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "text",
              "value": "={{$node['Query AI Model'].json['choices'][0]['message']['content']}}"
            },
            {
              "name": "voice",
              "value": "English-US.Female-1"
            }
          ]
        },
        "options": {
          "response": {
            "response": {
              "responseFormat": "file"
            }
          }
        }
      }
    },
    {
      "name": "Return Audio Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "position": [1120, 300],
      "parameters": {
        "respondWith": "binary",
        "binaryData": "={{$node['Convert Response to Speech'].binary.data}}",
        "options": {
          "responseHeaders": {
            "entries": [
              {
                "name": "Content-Type",
                "value": "audio/wav"
              },
              {
                "name": "Content-Disposition",
                "value": "attachment; filename=ai_response.wav"
              }
            ]
          }
        }
      }
    }
  ]
}
```

## Advanced Configuration

### Engine Selection Strategies

1. **Auto Mode (Recommended)**:
   - Tries NVIDIA Riva first for best quality
   - Falls back to pyttsx3 if Riva is unavailable
   - Provides reliable service continuity

2. **Specific Engine Selection**:
   - `"engine": "riva"` - Force NVIDIA Riva (cloud/local)
   - `"engine": "pyttsx3"` - Force local pyttsx3 TTS
   - `"engine": "edge"` - Force Microsoft Edge TTS

### Voice Options

For NVIDIA Riva TTS:
- `"English-US.Female-1"` - Default female voice
- `"English-US.Male-1"` - Male voice option
- Custom voices (if configured in your Riva setup)

### Environment Variables

Configure these in your `.env` file:

```env
# NVIDIA Riva Configuration
NVIDIA_RIVA_API_KEY=your_api_key_here
RIVA_SERVER=grpc.nvcf.nvidia.com:443

# Speech API Server
SPEECH_API_PORT=8001
```

## Error Handling in n8n

Add error handling to your workflows:

```json
{
  "name": "Error Handler",
  "type": "n8n-nodes-base.errorTrigger",
  "parameters": {
    "errorWorkflows": [
      {
        "workflow": "Speech Service Fallback"
      }
    ]
  }
}
```

## Performance Tips

1. **Audio Format**: Use WAV format for best compatibility
2. **File Size**: Keep audio files under 10MB for faster processing
3. **Sample Rate**: 16kHz or 22kHz work well for most use cases
4. **Caching**: Store frequently used audio in the shared folder

## Troubleshooting

### Common Issues

1. **"No TTS engines available"**:
   - Check if the speech API server is running
   - Verify pyttsx3 is installed: `pip install pyttsx3`
   - Check NVIDIA Riva connection

2. **Empty audio files**:
   - Verify the text content is not empty
   - Check the voice parameter is valid
   - Try switching engines

3. **Connection refused**:
   - Ensure the speech API server is running on port 8001
   - Check firewall settings
   - Verify n8n can reach localhost:8001

### Debug Commands

```bash
# Check service health
curl http://localhost:8001/health

# List available engines
curl http://localhost:8001/engines

# Test TTS directly
curl -X POST "http://localhost:8001/text-to-speech" \
  -H "Content-Type: application/json" \
  -d '{"text":"Test message","engine":"pyttsx3"}' \
  --output debug_test.wav
```

## Next Steps

1. **Custom Voices**: Configure additional voices in Riva
2. **Language Support**: Add multi-language capabilities
3. **Real-time Streaming**: Implement WebSocket streaming for live conversations
4. **Voice Cloning**: Integrate custom voice training workflows

## Support

For issues and questions:
1. Check the server logs in the terminal where you started the speech API
2. Verify your environment variables are correctly set
3. Test individual components (TTS, ASR) separately
4. Review the n8n execution logs for detailed error messages

---

*This integration enables powerful voice-controlled AI workflows with your self-hosted infrastructure.*
