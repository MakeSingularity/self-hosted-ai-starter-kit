# Oliver Workflow Voice Message Integration Guide

## Overview

This guide shows how to integrate the Whisper Speech Recognition API with Oliver's existing Telegram workflow to handle voice messages.

## Current Oliver Workflow State

✅ **Functional**: Oliver responds to text messages  
❌ **Missing**: Voice message handling  
🎯 **Goal**: Add speech-to-text transcription for voice messages  

## Integration Steps

### Step 1: Add Message Type Detection

Add a **Switch** node after the Telegram trigger to route different message types:

**Node: "Message Type Router"**
- **Type**: Switch
- **Mode**: Rules
- **Rules**:
  1. **Voice Messages**: `{{ $json.message.voice !== undefined }}`
  2. **Audio Messages**: `{{ $json.message.audio !== undefined }}`
  3. **Text Messages**: `{{ $json.message.text !== undefined }}` (fallback)

**Optional: Add Set Node for Voice/Audio Messages**
If you want to add metadata, add a **Set** node after voice/audio routes:

**Node: "Prepare Voice Data"** (for voice route)
- **Type**: Set
- **Values**:
  - `message_type`: `voice`
  - `needs_transcription`: `true`
  - `file_id`: `{{ $json.message.voice.file_id }}`
  - `duration`: `{{ $json.message.voice.duration }}`
  - `mime_type`: `{{ $json.message.voice.mime_type || 'audio/ogg' }}`

### Step 2: Add Transcription Service

Add HTTP Request node for Whisper API:

**Node: "Transcribe Voice Message"**
- **Type**: HTTP Request
- **Method**: POST
- **URL**: `http://host.docker.internal:8000/transcribe/n8n` ✅ **CONFIRMED WORKING**
- **Authentication**: None
- **Send Query Parameters**: No
- **Send Headers**: Yes
- **Headers**: 
  ```json
  {
    "Content-Type": "application/json"
  }
  ```
- **Send Body**: Yes
- **Body Content Type**: JSON
- **Body (JSON format)**:
  ```json
  {
    "message": "{{ $json.original_message }}",
    "message_type": "{{ $json.message_type }}",
    "file_id": "{{ $json.file_id }}",
    "duration": "{{ $json.duration }}"
  }
  ```

**⚠️ Docker Network Note**: Since n8n runs in Docker, use `host.docker.internal:8000` instead of `localhost:8000` to reach services running on your host machine.

**Alternative Body Format (if using raw JSON):**
- **Body Content Type**: Raw/Text
- **Body**:
  ```javascript
  {{ JSON.stringify({
    message: $json.original_message,
    message_type: $json.message_type,
    file_id: $json.file_id,
    duration: $json.duration
  }) }}
  ```

### Step 3: Add Merge Node

After transcription, use a **Merge** node to combine voice and text paths:

**Node: "Merge Messages"**
- **Type**: Merge
- **Mode**: "Merge By Position"
- **Inputs**: 
  - Input 1: From "Transcribe Voice Message" 
  - Input 2: From "Prepare Text Data"

### Step 4: Update Message Processing

Add a **Function** node after the merge to standardize the message format:

**Node: "Process Message Content"**
- **Type**: Function  
- **Code**:
```javascript
// Extract text content from either transcription or original message
const item = items[0].json;

let messageText = '';
let messageSource = '';

if (item.needs_transcription && item.transcription) {
  // Use transcribed text from voice/audio
  messageText = item.transcription.text;
  messageSource = `voice_message (${item.message_type}, ${item.duration}s)`;
  
  // Add transcription confidence if available
  if (item.transcription.confidence) {
    messageSource += ` [confidence: ${Math.round(item.transcription.confidence * 100)}%]`;
  }
} else {
  // Use original text message
  messageText = item.processed_text || item.original_message?.text || '';
  messageSource = 'text_message';
}

return [{
  json: {
    processed_text: messageText,
    message_source: messageSource,
    user_id: item.original_message.from.id,
    username: item.original_message.from.username || item.original_message.from.first_name,
    timestamp: new Date().toISOString(),
    chat_id: item.original_message.chat.id
  }
}];
```

### Step 5: Update Oliver's AI Processing

Use the **AI Agent** node (recommended) for cleaner integration:

**Node: "Oliver AI Response"**
- **Type**: AI Agent
- **Chat Model**: Ollama Chat Model
- **Base URL**: `http://ollama:11434`
- **Model**: `llama3.1:latest`
- **System Message**:
  ```
  You are Oliver, a helpful AI assistant. 
  
  When responding to voice messages, acknowledge that you heard their voice message. If the transcription seems unclear, politely ask for clarification.
  
  Current message source: {{ $json.message_source }}
  ```
- **Prompt**: `{{ $json.processed_text }}`
- **Options**:
  - **Temperature**: 0.7
  - **Max Tokens**: 1000

**Benefits of AI Agent node:**
- ✅ Built-in Ollama integration
- ✅ Automatic error handling
- ✅ Cleaner configuration
- ✅ Support for system prompts
- ✅ Optional output parsing

## Complete Workflow Structure

```
Telegram Trigger
    ↓
Message Type Router (Switch Node)
    ├── Voice Route → Prepare Voice Data (Set) → Transcribe Voice Message (HTTP Request)
    ├── Audio Route → Prepare Audio Data (Set) → Transcribe Voice Message (HTTP Request)  
    └── Text Route → Process Text Message (Set)
                    ↓
                Merge (Join) Node
                    ↓
            Process Message Content (Function)
                    ↓
            Oliver AI Response (AI Agent)
                    ↓
            Format Response (Set)
                    ↓
            Send Response (Telegram)
```

## n8n Node Configuration

### Switch Node Setup

**Node: "Message Type Router"**
- **Type**: Switch
- **Data Type**: Object
- **Property Name**: `message`
- **Rules**:
  1. **Rule 1 (Voice)**: 
     - **Operation**: "Object Key Exists"
     - **Value**: `voice`
     - **Output**: Connect to "Prepare Voice Data"
  
  2. **Rule 2 (Audio)**:
     - **Operation**: "Object Key Exists" 
     - **Value**: `audio`
     - **Output**: Connect to "Prepare Audio Data"
  
  3. **Rule 3 (Text - Fallback)**:
     - **Operation**: "Object Key Exists"
     - **Value**: `text`
     - **Output**: Connect to "Process Text Message"

### Set Nodes for Data Preparation

**Node: "Prepare Voice Data"** (Voice route)
- **Type**: Set
- **Keep Only Set**: false
- **Values**:
  - `message_type` = `voice`
  - `needs_transcription` = `true`
  - `file_id` = `{{ $json.message.voice.file_id }}`
  - `duration` = `{{ $json.message.voice.duration }}`
  - `original_message` = `{{ $json.message }}`

**Node: "Prepare Text Data"** (Text route)  
- **Type**: Set
- **Keep Only Set**: false
- **Values**:
  - `message_type` = `text`
  - `needs_transcription` = `false`
  - `processed_text` = `{{ $json.message.text }}`
  - `original_message` = `{{ $json.message }}`

### Error Handling

Add error handling for transcription failures:

**Node: "Transcription Error Handler"**
```javascript
// Handle transcription errors gracefully
if ($json.transcription && $json.transcription.error) {
  return [{
    json: {
      processed_text: "I received your voice message but couldn't transcribe it. Could you please send it as text?",
      message_source: "transcription_error",
      error_details: $json.transcription.error
    }
  }];
}
```

## Testing Scenarios

### 1. Text Message
- **Input**: "Hello Oliver"
- **Flow**: Telegram → Detect Type → Process Content → AI Response
- **Expected**: Normal text response

### 2. Voice Message
- **Input**: Voice recording saying "What's the weather?"
- **Flow**: Telegram → Detect Type → Transcribe → Process Content → AI Response
- **Expected**: "I heard your voice message asking about the weather..."

### 3. Transcription Error
- **Input**: Unclear voice message
- **Flow**: Telegram → Detect Type → Transcribe (fails) → Error Handler
- **Expected**: Polite request to resend as text

## Environment Setup

### Start Whisper API
```bash
cd "c:\AI Projects\self-hosted-ai-starter-kit"
python scripts/start_whisper_api.py
```

### Verify Services
```bash
# Check Whisper API
curl http://localhost:8000/status

# Check Ollama
docker exec ollama ollama list

# Check n8n
docker ps | grep n8n
```

## Backup & Deployment

### Export Current Workflow
1. Open n8n at http://localhost:5678
2. Select Oliver workflow
3. Click "Download" to backup current version
4. Save as `Oliver_backup_pre_voice.json`

### Import Modified Workflow
1. Create new workflow or duplicate existing
2. Add the new nodes as described above
3. Test with both text and voice messages
4. Deploy once confirmed working

## Monitoring & Debugging

### Whisper API Logs
Monitor transcription performance:
```bash
# Watch API logs
docker logs -f n8n

# Check transcription accuracy
python scripts/test_whisper_api.py
```

### n8n Execution Logs
- Enable "Save Execution Log" in n8n settings
- Monitor workflow executions for errors
- Check transcription success rates

## Performance Optimization

### Model Selection
- **Large Model**: Better accuracy, slower (~2-3s)
- **Tiny Model**: Faster processing (~0.5s), lower accuracy
- **Auto-fallback**: API automatically tries both

### Caching (Future Enhancement)
- Cache common phrases/responses
- Store transcription results
- Implement user-specific voice profiles

## Security Considerations

- Whisper API runs locally (no external data sharing)
- Voice messages processed locally via Ollama
- No audio data stored permanently
- Standard Telegram security applies

## Troubleshooting

### Common Issues

1. **Transcription API not responding**
   ```bash
   python scripts/start_whisper_api.py
   ```

2. **"Model not available" errors**
   ```bash
   docker exec ollama ollama pull ZimaBlueAI/whisper-large-v3:latest
   ```

3. **n8n workflow execution fails**
   - Check HTTP Request node configuration
   - Verify Whisper API is running on port 8000
   - Check n8n logs for detailed error messages

4. **Poor transcription quality**
   - Ensure clear audio input
   - Check microphone quality
   - Consider using large model for better accuracy

### Debug Mode

Enable detailed logging in n8n:
1. Go to Settings → Log Level
2. Set to "debug"
3. Monitor execution logs for detailed information
