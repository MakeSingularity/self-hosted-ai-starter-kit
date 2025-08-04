# 🤖 Enhanced AI System Monitor & Oliver Integration Guide

## 🎯 Overview

This enhanced monitoring workflow provides comprehensive health checks for our AI infrastructure and specific readiness assessments for Text-to-Speech (TTS) and Speech-to-Text (STT) capabilities that Oliver will need for voice interactions.

## 🚀 Features

### ✅ **System Health Monitoring**
- **Real-time System Metrics**: CPU, memory, disk usage, GPU availability
- **Service Status**: PostgreSQL, Ollama, Qdrant, n8n health checks
- **Docker Container Monitoring**: Service status and health
- **Python Integration**: Validation of Python environment and packages

### 🎙️ **TTS/STT Readiness Assessment**
- **Model Availability**: Checks for Whisper (STT) and Bark/Tortoise (TTS) models
- **Audio Dependencies**: Validates audio processing libraries
- **Hardware Readiness**: GPU acceleration and memory requirements
- **Real-time Processing**: Capability assessment for live voice interactions

### 🤖 **Oliver Integration Features**
- **Voice Interface Readiness**: Complete assessment of voice conversation capabilities
- **Brain Status**: LLM model availability and health
- **Memory System**: Vector database (Qdrant) status for Oliver's memory
- **Automation Health**: n8n workflow system status
- **Conversational Reports**: Human-friendly status summaries

## 📊 **Workflow Structure**

### **Triggers:**
1. **Manual Trigger**: On-demand health checks
2. **Scheduled Trigger**: Automatic checks every 6 hours (00:00, 06:00, 12:00, 18:00)
3. **Webhook API**: `GET /webhook/health-check` for programmatic access

### **Monitoring Nodes:**
1. **System Metrics Collection**
2. **GPU Capability Detection** 
3. **Docker Services Status**
4. **PostgreSQL Health Check**
5. **Ollama Models Check**
6. **Qdrant Vector DB Check**
7. **n8n API Health Check**

### **Analysis & Reporting:**
1. **Enhanced System Analysis**: Comprehensive AI-powered analysis
2. **Oliver Report Generation**: Conversational status summaries
3. **Critical Alert Detection**: Automatic notifications for urgent issues
4. **Report Persistence**: JSON and human-readable reports saved to `/shared/`

## 🔧 **Installation & Setup**

### **1. Import the Enhanced Workflow**
```bash
# Copy the enhanced workflow to n8n
cp enhanced-ai-monitoring-workflow.json n8n/demo-data/workflows/

# Restart n8n to load the new workflow
docker-compose restart n8n
```

### **2. Workflow Import in n8n**
1. Open n8n at `http://localhost:5678`
2. Go to **Workflows** → **Import from file**
3. Select `enhanced-ai-monitoring-workflow.json`
4. Activate the workflow

### **3. Set Up TTS/STT Models** (For Oliver Voice Capabilities)
```bash
# Install Whisper for Speech-to-Text
docker exec ollama ollama pull whisper:base

# Install Bark for Text-to-Speech  
docker exec ollama ollama pull bark

# Install LLM for Oliver's brain
docker exec ollama ollama pull llama3.2:latest

# Optional: Install audio processing dependencies
docker exec n8n pip install pyaudio speechrecognition pyttsx3
```

## 📈 **Usage**

### **Manual Health Check**
1. Open the workflow in n8n
2. Click the **Manual Trigger** node
3. Click **Execute Workflow**
4. View results in the workflow execution

### **API Access** 
```bash
# Get current system status
curl http://localhost:5678/webhook/health-check

# Response includes Oliver-friendly status
{
  "greeting": "Hello! I'm reporting on our AI system status...",
  "system_status": {
    "overall_health": "excellent",
    "voice_readiness": "Voice capabilities need setup...",
    "brain_status": "My brain is online and ready!",
    "memory_status": "My memory systems are operational...",
    "automation_status": "My automation capabilities are active..."
  },
  "capabilities_ready": {
    "text_conversation": true,
    "voice_conversation": false,
    "memory_recall": true,
    "task_automation": true,
    "system_monitoring": true
  }
}
```

### **Scheduled Monitoring**
The workflow automatically runs every 6 hours and:
- Saves detailed reports to `/shared/enhanced-system-status.json`
- Saves Oliver-friendly reports to `/shared/oliver-system-status.json`
- Triggers critical alerts if issues are detected

## 📋 **Report Files**

### **Enhanced System Status** (`/shared/enhanced-system-status.json`)
Complete technical report including:
- System performance metrics
- Service health status
- TTS/STT readiness scores
- Hardware capabilities
- Detailed recommendations

### **Oliver Status Report** (`/shared/oliver-system-status.json`)
Conversational report for Oliver including:
- Human-friendly status descriptions
- Voice interface readiness
- Capability assessments
- Performance metrics
- Next steps and recommendations

## 🎙️ **TTS/STT Readiness Checker**

### **Standalone Script**
```bash
# Run the TTS/STT readiness checker
docker exec n8n python /app/shared/tts_stt_checker.py
```

### **Readiness Categories**
- **Grade A (90-100%)**: Fully ready for voice interactions
- **Grade B (75-89%)**: Ready with minor optimizations needed  
- **Grade C (60-74%)**: Partially ready, missing key components
- **Grade D (0-59%)**: Not ready, major setup required

### **Key Components Checked**
1. **Ollama Service**: Running and accessible
2. **STT Models**: Whisper models available
3. **TTS Models**: Bark/Tortoise models available  
4. **LLM Models**: Conversational models for Oliver
5. **Audio Dependencies**: Python audio libraries
6. **Audio Devices**: Hardware audio capability

## 🤖 **Oliver Integration**

### **Voice Conversation Readiness**
Oliver can handle voice conversations when:
- ✅ Whisper model available (STT)
- ✅ Bark/TTS model available (TTS)
- ✅ LLM model available (conversation)
- ✅ Audio dependencies installed
- ✅ System performance adequate

### **Integration Points**
1. **Health Status API**: Oliver can query system health
2. **Capability Detection**: Oliver knows what features are available
3. **Performance Monitoring**: Oliver can detect system stress
4. **Service Dependencies**: Oliver understands service relationships

### **Oliver Workflow Integration**
```json
// Example of how Oliver can check if voice is ready
{
  "webhook_data": {
    "ready_for_voice": true,
    "brain_online": true,
    "system_health": 0.95,
    "needs_attention": false,
    "last_check": "2025-08-04T03:09:18.898Z"
  }
}
```

## 🚨 **Critical Alert System**

### **Alert Levels**
- **Critical**: Immediate action required (high CPU/memory, service failures)
- **Warning**: Monitor and plan action (low disk space, some services down)
- **Info**: Informational status updates

### **Alert Actions**
- Automatic detection of critical issues
- Structured alert notifications
- Recommended remediation steps
- Integration ready for external notification systems

## 🔮 **Future Enhancements**

### **Planned Features**
1. **Audio Device Detection**: Real-time microphone/speaker detection
2. **Model Performance Metrics**: TTS/STT quality and speed measurements
3. **Voice Training Status**: Custom voice model training progress
4. **Multi-language Support**: TTS/STT capability in multiple languages
5. **Real-time Audio Monitoring**: Live audio processing health checks

### **Oliver Expansion Points**
1. **Emotional State Monitoring**: Detecting Oliver's conversational mood
2. **Learning Progress Tracking**: Oliver's knowledge acquisition metrics
3. **Interaction Quality**: Voice conversation success rates
4. **Personality Calibration**: Oliver's response style optimization

## 📞 **Support & Troubleshooting**

### **Common Issues**
1. **Ollama Not Responding**: Check `docker-compose ps` and restart if needed
2. **Models Not Found**: Verify model installation with `ollama list`
3. **Audio Dependencies Missing**: Install with `pip install pyaudio speechrecognition pyttsx3`
4. **High Memory Usage**: Monitor with the system metrics in the reports

### **Debug Commands**
```bash
# Check all services
docker-compose ps

# Check Ollama models
docker exec ollama ollama list

# Test Python audio
docker exec n8n python -c "import pyaudio; print('Audio OK')"

# View latest system report
docker exec n8n cat /app/shared/oliver-system-status.json
```

---

**🎉 Ready to enhance Oliver's capabilities with comprehensive system monitoring and voice interaction readiness!**
