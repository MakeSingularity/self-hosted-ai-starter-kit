# 🚀 Hybrid AI Starter Kit - NVIDIA + n8n Edition

<div align="center">

**The Ultimate Self-Hosted AI Platform with Voice Intelligence**

![MakeSingularity - Enhanced AI Platform](https://raw.githubusercontent.com/MakeSingularity/self-hosted-ai-starter-kit/main/assets/n8n-demo.gif)

[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![NVIDIA](https://img.shields.io/badge/NVIDIA-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://nvidia.com)
[![n8n](https://img.shields.io/badge/n8n-FF6D5A?style=for-the-badge&logo=n8n&logoColor=white)](https://n8n.io)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

*Enhanced with NVIDIA Riva Speech Services, Advanced Python Integration, and Production-Ready Automation*

</div>

---

## ⚡ **Quick Start - Zero Errors Setup**

### 🎯 **New User? Start Here!**

**Option 1: Guided Setup (Recommended)**
```bash
# 1. Run the setup verification
python verify_setup.py

# 2. Or use the interactive quick start
python quick_start.py
```

**Option 2: Manual Setup**
```bash
# 1. Install basic requirements
pip install fastapi uvicorn pydantic python-dotenv requests numpy

# 2. Start Docker services
docker-compose up -d

# 3. Run the API server
python examples/api_server.py

# 4. Open n8n: http://localhost:5678
```

### 🚨 **Troubleshooting Common Issues**

| Issue | Quick Fix |
|-------|-----------|
| ❌ Import errors | Run `python verify_setup.py` |
| ❌ Docker not found | Install [Docker Desktop](https://www.docker.com/products/docker-desktop) |
| ❌ Python version | Ensure Python 3.8+ is installed |
| ❌ Port conflicts | Check if ports 5678, 8000, 8001 are available |

### 🎉 **Success Indicators**
- ✅ n8n running at: `http://localhost:5678`
- ✅ API docs at: `http://localhost:8000/docs`
- ✅ No import errors in terminal

---

## 🎯 **What Makes This Special**

This isn't just another AI starter kit - it's a **production-ready hybrid platform** that combines the best of cloud and local AI technologies:

### 🎤 **Speech-Enabled AI Workflows**
- **NVIDIA Riva Integration**: Enterprise-grade text-to-speech and speech-to-text
- **Hybrid Fallback System**: Local pyttsx3 TTS when cloud services are unavailable
- **Voice-Interactive Assistants**: Create AI that you can talk to and that talks back
- **Audio Content Generation**: Convert text to professional audio content

### 🧠 **Advanced AI Stack**
- **Ollama LLMs**: Local language models with GPU acceleration
- **NVIDIA Cloud Services**: Access to cutting-edge speech AI capabilities
- **Qdrant Vector Database**: Semantic search and RAG applications  
- **n8n Automation**: 400+ integrations for workflow automation

### 🐍 **Python-First Integration**
- **Conda Environment**: Isolated AI/ML environment with 40+ packages
- **FastAPI Servers**: Production-ready APIs for n8n integration
- **Shared File System**: Seamless data exchange between Python and n8n
- **One-Click Setup**: Automated installation and configuration

---

## 🛠️ **Complete Technology Stack**

### 🎯 **Core Platform**
| Component | Description | What It Enables |
|-----------|-------------|-----------------|
| 🤖 **[n8n](https://n8n.io/)** | Low-code automation platform | Visual workflows, 400+ integrations, AI nodes |
| 🧠 **[Ollama](https://ollama.com/)** | Local LLM runtime | Private AI models, GPU acceleration |
| 🗄️ **[Qdrant](https://qdrant.tech/)** | Vector database | Semantic search, RAG, embeddings |
| 🐘 **[PostgreSQL](https://postgresql.org/)** | Relational database | Structured data, n8n workflows |

### 🎤 **Speech AI Services**
| Component | Description | Integration |
|-----------|-------------|-------------|
| 🎯 **NVIDIA Riva** | Cloud speech services | Professional TTS/ASR via API |
| 🔊 **pyttsx3** | Local TTS engine | Reliable fallback speech synthesis |
| 🎚️ **Hybrid Speech API** | Multi-engine wrapper | FastAPI server for n8n workflows |
| 📁 **Audio Processing** | File handling system | WAV/MP3 support, streaming responses |

### 🐍 **Python AI Environment**
| Package Category | Key Libraries | Use Cases |
|------------------|---------------|-----------|
| **AI/ML Core** | `transformers`, `torch`, `numpy` | Model inference, data processing |
| **Speech Processing** | `soundfile`, `librosa`, `nvidia-riva-client` | Audio analysis, speech services |
| **Web APIs** | `fastapi`, `uvicorn`, `requests` | API servers, n8n integration |
| **Data Science** | `pandas`, `scikit-learn`, `matplotlib` | Analysis, visualization |

---

## 🚀 **What You Can Build**

### 🎙️ **Voice-Powered Applications**
- **🗣️ Voice Assistants**: Conversational AI with speech I/O
- **📻 Podcast Generation**: Convert articles to professional audio
- **🔊 Audio Notifications**: Voice alerts for automation workflows  
- **♿ Accessibility Tools**: Text-to-speech for visually impaired users

### 🤖 **Advanced AI Workflows**
- **📄 Document Intelligence**: PDF analysis with voice summaries
- **💬 Smart Chatbots**: Multi-modal communication (text + voice)
- **🔍 Semantic Search**: Vector-powered content discovery
- **📊 Data Analysis**: Python-powered insights via n8n

### 🏢 **Enterprise Solutions**
- **🎧 Customer Service**: Voice-enabled support automation
- **📱 IoT Integration**: Voice control for smart devices
- **📈 Business Intelligence**: Automated reporting with speech
- **🔐 Secure AI**: Private, on-premises AI processing

---

## ⚡ **Quick Start Guide**

### 🎯 **One-Click Installation**

Choose your platform and let our automated setup handle everything:

#### 🪟 **Windows (PowerShell)**
```powershell
# 🚀 Quick start with GPU acceleration
git clone https://github.com/MakeSingularity/self-hosted-ai-starter-kit.git
cd self-hosted-ai-starter-kit

# 🎯 One-click setup (CPU + Speech Services)
.\setup.ps1

# 🚀 GPU-accelerated setup (Recommended for NVIDIA users)
.\setup.ps1 -Profile gpu-nvidia
```

#### 🐧 **Linux/macOS (Bash)**
```bash
# 🚀 Clone the enhanced repository
git clone https://github.com/MakeSingularity/self-hosted-ai-starter-kit.git
cd self-hosted-ai-starter-kit

# 🔧 Make executable and setup
chmod +x setup.sh

# 🎯 CPU setup with speech services
./setup.sh

# 🚀 GPU setup for NVIDIA systems
./setup.sh --profile gpu-nvidia
```

### 🎉 **What the Setup Script Does**

Our automated setup provides a complete AI platform in minutes:

```
🔍 Prerequisites Check
  ├── ✅ Docker & Docker Compose
  ├── ✅ NVIDIA GPU drivers (if applicable)
  ├── ✅ Python & Conda
  └── ✅ Git configuration

🐍 Python Environment Setup
  ├── ✅ Creates 'ai-starter-kit' conda environment
  ├── ✅ Installs 40+ AI/ML packages
  ├── ✅ Configures NVIDIA Riva client
  └── ✅ Sets up speech processing libraries

🐳 Docker Services Deployment
  ├── ✅ n8n workflow automation
  ├── ✅ Ollama LLM runtime
  ├── ✅ Qdrant vector database
  ├── ✅ PostgreSQL database
  └── ✅ Shared volume configuration

🎤 Speech Services Integration
  ├── ✅ NVIDIA Riva API configuration
  ├── ✅ Local TTS fallback setup
  ├── ✅ FastAPI speech server
  └── ✅ Audio processing pipeline

🌐 Service URLs & Access
  ├── 📊 n8n Dashboard: http://localhost:5678
  ├── 🎤 Speech API: http://localhost:8001
  ├── 🧠 AI API Server: http://localhost:8000
  └── 📚 API Documentation: Auto-generated
```

---

## 🎤 **Speech Services Integration**

### 🔥 **Hybrid Speech Architecture**

Our platform features a unique multi-engine speech system:

```
n8n Workflow → Speech API Server (:8001) → [NVIDIA Riva Cloud]
                     ↓                      [Local pyttsx3 TTS]
               Audio Output ←─────────────── [Microsoft Edge TTS]
```

### 🎯 **Available Speech APIs**

| Endpoint | Method | Description | Example Use Case |
|----------|--------|-------------|------------------|
| `/health` | GET | Service status | Monitor speech engine availability |
| `/engines` | GET | List available TTS/ASR | Choose optimal engine for workflow |
| `/text-to-speech` | POST | Convert text to audio | Generate voice notifications |
| `/speech-to-text` | POST | Convert audio to text | Process voice commands |

### 🚀 **Quick Speech Test**

```bash
# 🎤 Test text-to-speech with automatic engine selection
curl -X POST "http://localhost:8001/text-to-speech" \
  -H "Content-Type: application/json" \
  -d '{"text":"Welcome to your AI-powered platform!","engine":"auto"}' \
  --output welcome.wav

# 🎧 Test with specific engine
curl -X POST "http://localhost:8001/text-to-speech" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from NVIDIA Riva!","engine":"riva"}' \
  --output riva_test.wav
```

---

## 🐍 **Python Environment Deep Dive**

### 🔧 **Pre-Configured AI Environment**

Our `ai-starter-kit` conda environment includes everything for serious AI development:

<details>
<summary><b>📦 Complete Package List (40+ packages)</b></summary>

```yaml
AI/ML Frameworks:
  - transformers: Hugging Face model library
  - torch: PyTorch deep learning
  - numpy: Numerical computing
  - scikit-learn: Machine learning toolkit

Speech & Audio:
  - nvidia-riva-client: NVIDIA speech services
  - pyttsx3: Local text-to-speech
  - soundfile: Audio file I/O
  - librosa: Audio analysis

Web & APIs:
  - fastapi: Modern API framework
  - uvicorn: ASGI server
  - requests: HTTP client
  - websockets: Real-time communication

Data Processing:
  - pandas: Data manipulation
  - matplotlib: Plotting
  - pillow: Image processing
  - python-dotenv: Environment management
```

</details>

### 🔌 **Integration Patterns**

| Integration Method | Use Case | Example |
|--------------------|----------|---------|
| **🌐 HTTP API Server** | n8n HTTP Request nodes | `POST http://localhost:8000/chat` |
| **⚡ Execute Command** | Direct Python execution | `python scripts/analyze.py` |
| **📁 Shared Files** | Data exchange | `/data/shared/results.json` |
| **🎤 Speech API** | Voice workflows | `POST http://localhost:8001/text-to-speech` |

### 🚀 **Ready-to-Use API Servers**

Start any of these servers for immediate n8n integration:

```bash
# 🧠 Main AI API Server (LLM, embeddings, analysis)
python examples/api_server.py
# Available at: http://localhost:8000

# 🎤 Speech Services API (TTS, ASR, voice processing)
python examples/hybrid_speech_api.py  
# Available at: http://localhost:8001

# 🔧 Custom API Server (your own endpoints)
python examples/custom_api_server.py
# Available at: http://localhost:8002
```

---

## 🎯 **Advanced Installation Options**

### 🖥️ **Manual Docker Setup**

#### 🎯 **Clone and Configure**
```bash
git clone https://github.com/MakeSingularity/self-hosted-ai-starter-kit.git
cd self-hosted-ai-starter-kit
cp .env.example .env  # Configure your API keys and settings
```

#### 🚀 **NVIDIA GPU Users (Recommended)**

For maximum performance with GPU acceleration:

```bash
# 🔥 GPU-accelerated setup with speech services
docker compose --profile gpu-nvidia up -d

# 🎤 Start speech API server
conda activate ai-starter-kit
python examples/hybrid_speech_api.py &

# 🧠 Start main AI API server  
python examples/api_server.py &
```

> **🔧 First-time NVIDIA setup?** Follow the [NVIDIA Container Toolkit installation guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

#### 🍎 **macOS/Apple Silicon Users**

Apple Silicon Macs require a hybrid approach for optimal performance:

```bash
# 🍎 Option 1: Full containerized setup (CPU only)
docker compose --profile cpu up -d

# 🚀 Option 2: Local Ollama + containerized services (Recommended)
# Install Ollama locally from https://ollama.com
# Set OLLAMA_HOST=host.docker.internal:11434 in .env
docker compose up -d

# 🎤 Enable speech services
conda activate ai-starter-kit  
python examples/hybrid_speech_api.py
```

#### 🐧 **AMD GPU Users (Linux)**

```bash
# 🔥 AMD GPU acceleration
docker compose --profile gpu-amd up -d

# 🎤 Speech services
conda activate ai-starter-kit
python examples/hybrid_speech_api.py
```

#### 💻 **CPU-Only Systems**

```bash
# ⚡ Efficient CPU setup
docker compose --profile cpu up -d

# 🎤 Local speech processing
conda activate ai-starter-kit
python examples/hybrid_speech_api.py
```

---

## 🎯 **Getting Started with Your AI Platform**

### 🚀 **First Steps After Installation**

1. **🌐 Access n8n Dashboard**
   ```
   Open: http://localhost:5678
   Setup: Create your admin account
   Import: Use our pre-built workflows
   ```

2. **🎤 Test Speech Services**
   ```bash
   # Verify speech API is running
   curl http://localhost:8001/health
   
   # Test text-to-speech
   curl -X POST "http://localhost:8001/text-to-speech" \
     -H "Content-Type: application/json" \
     -d '{"text":"Hello AI world!","engine":"auto"}' \
     --output test.wav
   ```

3. **🧠 Try the AI API**
   ```bash
   # Test the main AI server
   curl http://localhost:8000/health
   
   # Chat with local LLM
   curl -X POST "http://localhost:8000/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -d '{"model":"llama3.2","messages":[{"role":"user","content":"Hello!"}]}'
   ```

### 📋 **Pre-Built Workflow Templates**

Import these ready-to-use workflows into n8n:

| Template | Description | Features |
|----------|-------------|----------|
| 🎤 **Voice Assistant** | Complete voice interaction | Speech → AI → Speech |
| 📄 **Document Processor** | PDF analysis with summaries | RAG + TTS output |
| 🔊 **Audio Content Creator** | Text to podcast converter | Batch processing |
| 🤖 **Smart Notifications** | Voice alerts system | Event-driven TTS |

### 🔧 **Configuration Guide**

#### 🎛️ **Environment Variables (.env)**

```bash
# 🎤 NVIDIA Riva Speech Services
NVIDIA_RIVA_API_KEY=your_api_key_here
RIVA_SERVER=grpc.nvcf.nvidia.com:443

# 🧠 AI Model Configuration  
OLLAMA_MODEL=llama3.2
EMBEDDING_MODEL=mxbai-embed-large

# 🔐 Security Settings
N8N_ENCRYPTION_KEY=your_secure_key
POSTGRES_PASSWORD=your_db_password

# 🌐 Service Ports
N8N_PORT=5678
SPEECH_API_PORT=8001
AI_API_PORT=8000
```

#### 🎯 **API Key Setup**

1. **NVIDIA Riva**: Get your API key from [NVIDIA NGC](https://catalog.ngc.nvidia.com/)
2. **Update .env**: Add your key to `NVIDIA_RIVA_API_KEY`
3. **Restart services**: `docker compose restart`

---

## 🎭 **Example Workflows & Use Cases**

### 🎤 **Voice-Powered Automation**

<details>
<summary><b>🗣️ Voice Assistant Workflow</b></summary>

```json
{
  "workflow": "Voice Assistant",
  "trigger": "Webhook (audio upload)",
  "steps": [
    "Speech-to-Text (NVIDIA Riva)",
    "Intent Analysis (Local LLM)",  
    "Action Execution (n8n nodes)",
    "Response Generation (AI)",
    "Text-to-Speech (Hybrid engine)"
  ],
  "output": "Audio response file"
}
```

**n8n Implementation:**
1. **Webhook Trigger**: Receive audio files
2. **HTTP Request**: `POST /speech-to-text` → transcript
3. **Ollama LLM**: Analyze intent and generate response
4. **HTTP Request**: `POST /text-to-speech` → audio
5. **Respond**: Return audio file

</details>

<details>
<summary><b>📄 Document Intelligence</b></summary>

```json
{
  "workflow": "Smart Document Processor",
  "trigger": "File upload or schedule",
  "steps": [
    "PDF Text Extraction",
    "Chunk & Embed (Qdrant)",
    "AI Summary Generation", 
    "Voice Summary Creation",
    "Multi-format Output"
  ],
  "outputs": ["Text summary", "Audio summary", "Vector embeddings"]
}
```

**Features:**
- 📊 Batch PDF processing
- 🔍 Semantic search integration
- 🎧 Audio summaries for accessibility
- 📱 Multi-channel delivery (email, Slack, voice)

</details>

### 🏢 **Enterprise Integrations**

| Integration | Use Case | Implementation |
|-------------|----------|----------------|
| **📧 Email + Voice** | Audio email summaries | IMAP + TTS API |
| **💬 Slack Bots** | Voice message processing | Slack API + Speech API |
| **🏠 IoT Control** | Voice-controlled devices | MQTT + Speech recognition |
| **📞 Call Center** | Automated voice responses | Twilio + NVIDIA Riva |

---

## 🔧 **Advanced Configuration**

### 🎛️ **Performance Optimization**

```bash
# 🚀 GPU Memory Optimization
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# 🎤 Speech Quality Settings
RIVA_SAMPLE_RATE=22050
RIVA_VOICE_QUALITY=high
TTS_ENGINE_PRIORITY=riva,pyttsx3,edge

# 🧠 LLM Performance
OLLAMA_NUM_PARALLEL=4
OLLAMA_MAX_LOADED_MODELS=3
```

### 🔐 **Security Configuration**

```bash
# 🔒 API Security
API_KEY_REQUIRED=true
CORS_ORIGINS=http://localhost:5678,https://yourdomain.com
RATE_LIMIT_PER_MINUTE=60

# 🛡️ Network Security
SPEECH_API_BIND=127.0.0.1
AI_API_BIND=127.0.0.1
N8N_SECURE_COOKIE=true
```

---

## 📈 **Monitoring & Troubleshooting**

### 🔍 **Health Checks**

```bash
# 🏥 Comprehensive system health
python verify_speech_setup.py

# 🎯 Individual service checks
curl http://localhost:5678/healthz    # n8n
curl http://localhost:8001/health     # Speech API
curl http://localhost:8000/health     # AI API
curl http://localhost:11434/api/tags  # Ollama
curl http://localhost:6333/health     # Qdrant
```

### 🐛 **Common Issues & Solutions**

<details>
<summary><b>🎤 Speech Services Issues</b></summary>

**Issue**: "No TTS engines available"
```bash
# Check engine status
curl http://localhost:8001/engines

# Restart speech server
conda activate ai-starter-kit
python examples/hybrid_speech_api.py
```

**Issue**: NVIDIA Riva connection failed
```bash
# Verify API key
echo $NVIDIA_RIVA_API_KEY

# Test direct connection
python test_riva_connection.py
```

</details>

<details>
<summary><b>🐳 Docker Issues</b></summary>

**Issue**: GPU not detected
```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
```

</details>

---

## 🚀 **Upgrading Your Platform**

### 🔄 **System Updates**

```bash
# 🐳 Update Docker containers
docker compose --profile gpu-nvidia pull
docker compose create && docker compose --profile gpu-nvidia up -d

# 🐍 Update Python environment
conda activate ai-starter-kit
pip install -r requirements.txt --upgrade

# 🎤 Update speech services
pip install nvidia-riva-client --upgrade
pip install pyttsx3 --upgrade
```

### 📦 **Adding New Components**

```bash
# 🧠 Install additional AI models
ollama pull mistral:7b
ollama pull codellama:13b

# 🎤 Add new TTS voices
# Update NVIDIA Riva voice configurations

# 🔧 Custom Python packages
conda activate ai-starter-kit
pip install your-custom-package
```

---

## 🤝 **Contributing & Community**

### 🌟 **Get Involved**

- 🐛 **Report Issues**: Use GitHub Issues for bugs and feature requests
- 🔧 **Submit PRs**: Contributions welcome for improvements
- 💬 **Join Discussions**: Share your AI workflows and get help
- 📚 **Documentation**: Help improve guides and examples

### 📖 **Documentation Links**

- 📘 **[Speech Integration Guide](SPEECH_INTEGRATION.md)**: Complete n8n integration examples
- 🐍 **[Python Integration Guide](examples/PYTHON_INTEGRATION.md)**: API server patterns
- 🔧 **[Setup Troubleshooting](SPEECH_IMPLEMENTATION_COMPLETE.md)**: Installation help
- 🎯 **[API Reference](http://localhost:8001/docs)**: Interactive API documentation

---

## 📜 **License**

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

**Built with ❤️ by [MakeSingularity](https://github.com/MakeSingularity)**

*Enhanced fork of the original n8n self-hosted AI starter kit with advanced speech capabilities and Python integration.*

---

<div align="center">

### 🎉 **Ready to Build Voice-Powered AI?**

**[⭐ Star this repo](https://github.com/MakeSingularity/self-hosted-ai-starter-kit)** • **[🍴 Fork it](https://github.com/MakeSingularity/self-hosted-ai-starter-kit/fork)** • **[📖 Read the docs](SPEECH_INTEGRATION.md)**

</div>
