# Enhanced Oliver Workflow with Speech Recognition

## 🎤 **Whisper Integration for Telegram Voice Messages**

### **Current Setup Status:**
- ✅ **Whisper Large v3** (849.7 MB) - High accuracy model
- ✅ **Whisper Tiny** (42.0 MB) - Fast processing model  
- ✅ **Ollama Integration** - Local, free processing
- ✅ **n8n Ready** - Workflow integration prepared

## 🔧 **Implementation Plan**

### **Phase 1: Basic Voice Message Handling**

**New Oliver Workflow Structure:**
1. **Telegram Trigger** (existing) → Receives messages
2. **Message Type Switch** (new) → Route text vs voice
3. **Whisper Speech Recognition** (new) → Convert voice to text
4. **Text Merge** (new) → Combine original text + transcribed voice
5. **AI Agent** (existing) → Process unified text input
6. **Telegram Response** (existing) → Send reply

### **Phase 2: Enhanced Audio Processing**

**Additional Features:**
- Audio format conversion (MP3, OGG, M4A → WAV)
- Quality assessment and enhancement
- Language detection
- Confidence scoring
- Fallback handling

## 📋 **n8n Workflow Modifications Needed**

### **1. Add Message Type Detection Node**

```javascript
// n8n Function Node: "Detect Message Type"
if ($json.message.voice) {
    return {
        json: {
            message_type: "voice",
            voice_data: $json.message.voice,
            original_message: $json.message,
            needs_transcription: true
        }
    };
} else if ($json.message.audio) {
    return {
        json: {
            message_type: "audio",
            audio_data: $json.message.audio,
            original_message: $json.message,
            needs_transcription: true
        }
    };
} else {
    return {
        json: {
            message_type: "text",
            text: $json.message.text,
            original_message: $json.message,
            needs_transcription: false
        }
    };
}
```

### **2. Add Whisper Transcription Node**

```javascript
// n8n HTTP Request Node: "Whisper Transcription"
// Method: POST
// URL: http://localhost:8000/transcribe  (we'll create this endpoint)
// Body:
{
    "file_id": "{{ $json.voice_data.file_id }}",
    "message_id": "{{ $json.original_message.message_id }}",
    "user_id": "{{ $json.original_message.from.id }}",
    "duration": "{{ $json.voice_data.duration }}"
}
```

### **3. Add Text Merging Node**

```javascript
// n8n Function Node: "Merge Text and Transcription"
let finalText = "";
let messageContext = "";

if ($json.message_type === "voice" || $json.message_type === "audio") {
    finalText = $json.transcription?.text || "Voice message could not be transcribed";
    messageContext = `User sent a ${$json.message_type} message (${$json.voice_data?.duration || 0}s): `;
} else {
    finalText = $json.text || "";
    messageContext = "User sent a text message: ";
}

return {
    json: {
        message: {
            text: finalText,
            from: $json.original_message.from,
            message_id: $json.original_message.message_id,
            context: messageContext
        },
        transcription_info: $json.transcription || null,
        original_type: $json.message_type
    }
};
```

## 🚀 **Quick Setup Steps**

### **Step 1: Create Whisper API Endpoint**

I'll create a simple FastAPI server that Oliver can call for transcription:

```python
# This will be our Whisper API server
from fastapi import FastAPI
from whisper_speech_recognition import WhisperSpeechRecognizer

app = FastAPI()
whisper = WhisperSpeechRecognizer()

@app.post("/transcribe")
async def transcribe_telegram_voice(request: dict):
    # Download Telegram file and transcribe
    result = whisper.process_telegram_voice_message(request)
    return result
```

### **Step 2: Update Oliver Workflow**

Add the new nodes to handle voice messages before they reach the AI Agent.

### **Step 3: Test with Voice Messages**

Send voice messages to Oliver via Telegram and verify transcription works.

## 🎯 **Expected User Experience**

### **Before (Text Only):**
User: Types "What's the weather like?"
Oliver: Responds with weather info

### **After (Voice + Text):**
User: 🎤 Says "What's the weather like?"
System: Transcribes → "What's the weather like?"
Oliver: Responds with weather info (same as text)

### **Enhanced Response:**
Oliver: "I heard you ask about the weather [🎤 voice message, 3s]..."

## 📊 **Performance Considerations**

### **Model Selection:**
- **Whisper Large v3**: High accuracy, ~2-5 seconds processing
- **Whisper Tiny**: Fast processing, ~0.5-1 second, slightly lower accuracy

### **Audio Quality Optimization:**
- Convert to 16kHz mono WAV for best results
- Handle various Telegram formats (OGG, MP3, M4A)
- Noise reduction for poor quality audio

### **Fallback Strategy:**
1. Try Ollama Whisper Large v3
2. If too slow, fall back to Whisper Tiny
3. If Ollama fails, use OpenAI Whisper locally
4. If all fail, respond with "Voice message received but could not transcribe"

## 🔍 **Integration with Existing Monitoring**

Our monitoring tools will track:
- Transcription success rates
- Processing times
- Audio quality metrics
- User satisfaction with voice responses

```bash
# Monitor voice message processing
python scripts/realtime_monitor.py live

# Check transcription performance
python scripts/ai_agent_debugger.py analyze --include-voice
```

This sets up a complete local, free speech recognition system that integrates seamlessly with your existing Oliver workflow!
