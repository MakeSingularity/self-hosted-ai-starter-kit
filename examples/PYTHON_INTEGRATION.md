# Python Integration with n8n

This guide explains how to use your local Python environment with n8n workflows.

## Architecture Overview

```
┌─────────────────┐    HTTP/Commands    ┌─────────────────┐
│   n8n (Docker)  │ ←──────────────→   │ Python (Local)  │
│                 │                     │                 │
│ • Workflows     │                     │ • AI Libraries  │
│ • HTTP Requests │                     │ • Custom Logic  │
│ • Execute Cmd   │                     │ • Riva Client   │
└─────────────────┘                     └─────────────────┘
```

## Integration Methods

### 1. HTTP API Server (Recommended for Production)

**Setup:**
1. Activate your environment: `conda activate ai-starter-kit`
2. Start the API server: `python examples/api_server.py`
3. Server runs on: `http://localhost:8000`

**In n8n:**
- Use **HTTP Request** nodes
- POST to `http://localhost:8000/process-text`
- JSON body: `{"text": "your text", "operation": "sentiment"}`

**Example n8n HTTP Request Node:**
```json
{
  "url": "http://localhost:8000/process-text",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "text": "{{ $json.input_text }}",
    "operation": "sentiment"
  }
}
```

### 2. Execute Command Node (Simple Scripts)

**In n8n:**
- Use **Execute Command** node
- Command: `conda run -n ai-starter-kit python /path/to/script.py --text "{{ $json.input }}"`

**Example Execute Command:**
```bash
conda run -n ai-starter-kit python "c:/AI Projects/self-hosted-ai-starter-kit/examples/python_integration_example.py" --text "{{ $json.text }}" --operation sentiment --output-format json
```

### 3. Shared File System

**Setup:**
- Python scripts write results to `/data/shared/` folder
- n8n reads results using **Read/Write Files from Disk** node

**Python writes:**
```python
import json
result = {"processed": True, "data": "result"}
with open("/data/shared/result.json", "w") as f:
    json.dump(result, f)
```

**n8n reads:**
```
Path: /data/shared/result.json
```

## Available Python Services

### Text Processing
- **Summarization**: Condense long text
- **Sentiment Analysis**: Determine emotional tone
- **Entity Extraction**: Find emails, phones, URLs

### AI/ML Operations
- **Vector Embeddings**: Using sentence-transformers
- **Document Processing**: PDF parsing, text extraction
- **Custom Models**: Load your trained models

### NVIDIA Riva Integration
- **Speech-to-Text**: Convert audio to text
- **Text-to-Speech**: Convert text to audio
- **NLP Services**: Advanced language processing

## Example Workflows

### 1. Document Analysis Pipeline
```
Trigger → Read PDF → HTTP Request (Python API) → Process Results → Store in Qdrant
```

### 2. Voice Assistant
```
Webhook → Riva STT → Ollama LLM → Riva TTS → Response
```

### 3. Email Sentiment Analysis
```
Email Trigger → Extract Text → Python Sentiment → Route Based on Score
```

## Best Practices

### Performance
- Keep Python API server running for faster responses
- Use async operations for heavy processing
- Cache results when possible

### Security
- Run API server on localhost only
- Validate all inputs in Python scripts
- Use environment variables for sensitive data

### Error Handling
- Always return JSON with status indicators
- Log errors for debugging
- Implement retries in n8n for reliability

## Troubleshooting

### Common Issues

**1. "conda: command not found"**
- Solution: Use full path to conda or activate environment first

**2. "Module not found" errors**
- Solution: Ensure you're using the correct conda environment

**3. API server not responding**
- Solution: Check if server is running on correct port
- Check firewall settings

### Debug Commands

```bash
# Check conda environment
conda info --envs

# Test Python script directly
conda run -n ai-starter-kit python examples/python_integration_example.py --text "test" --operation sentiment

# Test API server
curl -X POST "http://localhost:8000/process-text" -H "Content-Type: application/json" -d '{"text":"Hello world","operation":"sentiment"}'
```

## Next Steps

1. **Start simple**: Try the Execute Command method first
2. **Scale up**: Move to HTTP API for production workflows  
3. **Integrate Riva**: Add speech capabilities to your workflows
4. **Custom models**: Load your own AI models into the Python environment
