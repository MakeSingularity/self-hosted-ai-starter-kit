# 📁 Project Structure

This document outlines the organized structure of the Hybrid AI Starter Kit.

## 🗂️ **Root Directory**
```
self-hosted-ai-starter-kit/
├── 📄 README.md                    # Main project documentation
├── 📄 requirements.txt             # Python dependencies
├── 📄 docker-compose.yml           # Docker services configuration
├── 📄 .env.example                 # Environment variables template
├── 📄 .gitignore                   # Git ignore patterns
├── 🔧 setup.ps1                    # Windows setup script
├── 🔧 setup.sh                     # Linux/macOS setup script
├── 📜 LICENSE                      # Apache 2.0 license
├── 📜 CONTRIBUTING.md              # Contribution guidelines
├── 🗂️ assets/                      # Static assets (images, demos)
├── 🗂️ docs/                        # Documentation files
├── 🗂️ examples/                    # Python API servers and examples
├── 🗂️ n8n/                         # n8n workflow data and configs
├── 🗂️ shared/                      # Shared files between containers
└── 🗂️ tests/                       # Test scripts and utilities
```

## 📚 **Documentation (`docs/`)**
```
docs/
├── 📄 SPEECH_INTEGRATION.md        # Complete n8n speech integration guide
├── 📄 SPEECH_IMPLEMENTATION_COMPLETE.md  # Implementation summary
├── 📄 RIVA_SETUP_COMPLETE.md       # NVIDIA Riva setup guide
└── 📄 SETUP_COMPLETE.md            # General setup completion guide
```

## 🐍 **Python Examples (`examples/`)**
```
examples/
├── 📄 api_server.py                # Main AI API server for n8n integration
├── 📄 hybrid_speech_api.py         # Multi-engine speech services API
├── 📄 riva_api_server.py           # NVIDIA Riva-specific API server
├── 📄 riva_integration_example.py  # Complete Riva client wrapper
├── 📄 python_integration_example.py # Python integration patterns
├── 📄 PYTHON_INTEGRATION.md        # Python integration documentation
└── 📄 RIVA_INTEGRATION.md          # NVIDIA Riva integration guide
```

## 🧪 **Tests (`tests/`)**
```
tests/
├── 📄 verify_speech_setup.py       # Complete system verification
├── 📄 test_riva_connection.py      # NVIDIA Riva connectivity test
├── 📄 test_speech_services.py      # Speech services functionality test
└── 📄 test_nvidia_build_api.py     # NVIDIA Build API test
```

## 🐳 **Docker & Data (`n8n/`, `shared/`)**
```
n8n/
├── 🗂️ demo-data/                   # Sample workflows and credentials
└── ... (n8n internal data)

shared/
├── 🗂️ input/                       # Input files for processing
├── 🗂️ output/                      # Generated outputs (audio, text, etc.)
└── 🗂️ temp/                        # Temporary processing files
```

## 🎯 **Key Files Description**

### **🚀 Main API Servers**
- **`api_server.py`**: Primary AI API server with text processing, sentiment analysis, and entity extraction
- **`hybrid_speech_api.py`**: Speech services with NVIDIA Riva, pyttsx3 fallback, and audio processing
- **`riva_api_server.py`**: Dedicated NVIDIA Riva speech services server

### **🔧 Setup & Configuration**
- **`setup.ps1`/`setup.sh`**: Automated installation scripts
- **`requirements.txt`**: Complete Python package dependencies
- **`.env.example`**: Environment variables template

### **📖 Documentation**
- **`README.md`**: Main project documentation with setup and usage
- **`docs/SPEECH_INTEGRATION.md`**: Complete guide for n8n speech workflow integration
- **`examples/PYTHON_INTEGRATION.md`**: Python API integration patterns

### **🧪 Testing & Verification**
- **`tests/verify_speech_setup.py`**: Comprehensive system health check
- **`tests/test_riva_connection.py`**: NVIDIA Riva cloud service testing

## 🎵 **Usage Patterns**

### **For n8n Users**
1. Start API servers: `python examples/api_server.py` or `python examples/hybrid_speech_api.py`
2. Use HTTP Request nodes to call: `http://localhost:8000/` or `http://localhost:8001/`
3. Reference examples in `docs/SPEECH_INTEGRATION.md`

### **For Developers**
1. Review `examples/PYTHON_INTEGRATION.md` for integration patterns
2. Use `examples/` scripts as templates for custom APIs
3. Run `tests/verify_speech_setup.py` to validate installation

### **For System Administrators**
1. Use setup scripts for automated deployment
2. Monitor with health check endpoints
3. Configure environment variables in `.env`

## 🔄 **Maintenance**

### **Cleaning Up**
- Python cache: `find . -name "__pycache__" -exec rm -rf {} +`
- Test audio: `rm *.wav *.mp3` (if not needed)
- Logs: `rm *.log` (rotate as needed)

### **Updates**
- Dependencies: `pip install -r requirements.txt --upgrade`
- Docker images: `docker compose pull`
- n8n workflows: Import from `n8n/demo-data/`

---

*This structure provides a clean, organized foundation for your hybrid AI platform development.*
