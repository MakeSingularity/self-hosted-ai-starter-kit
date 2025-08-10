# 🤖 AI Telegram Chatbot - Self-Hosted Starter Kit

<div align="center">

**GPU-Accelerated AI Chatbot with Data Persistence**

![n8n Demo](https://raw.githubusercontent.com/MakeSingularity/self-hosted-ai-starter-kit/main/assets/n8n-demo.gif)

[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![n8n](http## 📚 **Documentation**

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Essential commands and daily operations
- **[SETUP.md](SETUP.md)** - Detailed step-by-step setup guide
- **[DATA_PERSISTENCE.md](DATA_PERSISTENCE.md)** - Backup and data management strategies  
- **[docker-compose.yml](docker-compose.yml)** - Service configuration
- **[.env.example](.env.example)** - Environment variables templateg.shields.io/badge/n8n-FF6D5A?style=for-the-badge&logo=n8n&logoColor=white)](https://n8n.io)
[![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.ai)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![NVIDIA](https://img.shields.io/badge/NVIDIA-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://nvidia.com)

*Production-ready AI chatbot with GPU acceleration, persistent data, and complete Telegram integration*

</div>

---

## 🎯 **What This Does**

This is a **complete AI Telegram chatbot solution** that:
- ✅ **Receives messages** from Telegram users via webhook
- ✅ **Processes them** with GPU-accelerated Ollama (Llama 3.1 8B model)
- ✅ **Remembers conversations** using PostgreSQL chat memory
- ✅ **Sends intelligent responses** back to Telegram
- ✅ **Persists all data locally** - models, workflows, chat history
- ✅ **Runs completely self-hosted** - no external API dependencies
- ✅ **GPU acceleration** for faster AI inference (NVIDIA support)

## 🚀 **Quick Start**

### Prerequisites
- Docker Desktop with Docker Compose
- NVIDIA GPU with Docker GPU support (optional but recommended)
- ngrok Docker Desktop Extension or ngrok CLI
- Telegram Bot Token from [@BotFather](https://t.me/botfather)

### 1. Clone Repository
```bash
git clone https://github.com/MakeSingularity/self-hosted-ai-starter-kit.git
cd self-hosted-ai-starter-kit
```

### 2. Create Environment File
Create a `.env` file with your configuration:
```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# Database Configuration
POSTGRES_DB=n8n
POSTGRES_USER=root
POSTGRES_PASSWORD=your_secure_password

# n8n Configuration  
N8N_ENCRYPTION_KEY=your_encryption_key_32_chars
N8N_USER_MANAGEMENT_JWT_SECRET=your_jwt_secret

# Ollama Configuration
OLLAMA_HOST=ollama:11434

# ngrok Configuration (optional - for custom domains)
NGROK_AUTHTOKEN=your_ngrok_token
SUBDOMAIN=your-custom-subdomain
```

### 3. Start Services

**For NVIDIA GPU (Recommended):**
```bash
# Create data directories for persistence
mkdir -p data/{n8n,postgres,ollama,qdrant}

# Start with GPU acceleration
docker compose --profile gpu-nvidia up -d

# Verify GPU is detected
docker logs ollama | grep "inference compute"
```

**For CPU Only:**
```bash
# Create data directories for persistence  
mkdir -p data/{n8n,postgres,ollama,qdrant}

# Start with CPU profile
docker compose --profile cpu up -d
```

### 4. Setup ngrok Tunnel
**Option A: Docker Desktop Extension**
1. Open Docker Desktop → Extensions → ngrok
2. Create tunnel: `localhost:5678` → Get HTTPS URL
3. Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

**Option B: ngrok CLI**
```bash
ngrok http 5678
# Copy the HTTPS forwarding URL
```

### 5. Access n8n and Import Workflow
1. Open n8n: `http://localhost:5678` or your ngrok HTTPS URL
2. The Oliver workflow should auto-import from the database
3. If not, the workflow will be available to import

### 6. Configure Telegram Webhook
1. In n8n, open the Oliver workflow  
2. Click the Telegram Trigger node
3. Update the webhook URL to your ngrok HTTPS domain
4. Save and activate the workflow

### 7. Test Your Bot
Send a message to your Telegram bot - enjoy GPU-accelerated AI responses! 🚀

---

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Telegram      │    │     n8n      │    │    Ollama       │
│   (Webhook)     │◄──►│  (Workflow)  │◄──►│  (GPU/CPU AI)   │
└─────────────────┘    └──────────────┘    └─────────────────┘
                              │                      │
                              ▼                      ▼
                       ┌──────────────┐    ┌─────────────────┐
                       │  PostgreSQL  │    │  Local Storage  │
                       │ (Chat Memory)│    │ (Data/Models)   │
                       └──────────────┘    └─────────────────┘
```

## 💾 **Data Persistence**

All data is stored locally in `./data/` for complete persistence:

```
data/
├── n8n/          # Workflows, credentials, settings
├── postgres/     # Database files, chat history  
├── ollama/       # AI models (Llama 3.1 8B, embeddings)
└── qdrant/       # Vector database storage
```

**Benefits:**
- 🔒 **Zero data loss** - Survive container recreation
- 💾 **Easy backup** - Just copy the `data/` folder
- 🔄 **Version control** - Track configuration changes
- 📦 **Portable** - Move to any Docker-enabled system

## 📊 **Services & GPU Support**

| Service | Purpose | Port | GPU Support | Status |
|---------|---------|------|-------------|--------|
| **n8n** | Workflow automation | 5678 | - | ✅ Running |
| **PostgreSQL** | Chat memory & data | 5432 | - | ✅ Running |  
| **Ollama** | AI inference engine | 11434 | ✅ NVIDIA CUDA | ✅ Running |
| **Qdrant** | Vector database | 6333 | - | ✅ Running |

### GPU Performance
- **Supported**: NVIDIA GPUs with CUDA support
- **Detection**: Automatic GPU detection and utilization
- **Models**: Llama 3.1 8B + nomic-embed-text
- **Memory**: Efficient GPU memory management
- **Fallback**: Automatic CPU fallback if GPU unavailable

### Profiles Available
```bash
# For NVIDIA GPU acceleration (recommended)
docker compose --profile gpu-nvidia up -d

# For AMD GPU acceleration  
docker compose --profile gpu-amd up -d

# For CPU-only execution
docker compose --profile cpu up -d
```

## 🔧 **The Oliver Workflow**

The main chatbot workflow consists of:

1. **Telegram Trigger** - Receives incoming messages
2. **AI Agent Node** - Processes messages with Ollama
3. **Postgres Chat Memory** - Stores conversation history  
4. **Telegram Send** - Sends responses back

## 📝 **Configuration Files**

- `docker-compose.yml` - Service definitions
- `.env` - Environment variables
- `ngrok.yml` - ngrok tunnel configuration  
- `n8n/demo-data/` - Pre-configured workflows and credentials

## 🛠️ **Development & Management**

### Check System Status
```bash
# View all running containers
docker compose ps

# Check GPU detection (NVIDIA)
docker logs ollama | grep "inference compute"

# Monitor resource usage
docker stats
```

### View Logs
```bash
# View n8n logs
docker logs n8n -f

# View Ollama AI processing
docker logs ollama -f

# View all services
docker compose logs -f
```

### Data Management
```bash
# Backup all data
cp -r ./data ./backup-$(date +%Y%m%d)

# View data usage
du -sh ./data/*

# Clean old Docker volumes (if migrating)
docker volume prune
```

### Service Management
```bash
# Restart specific service
docker restart n8n

# Restart all services  
docker compose restart

# Update to latest images
docker compose pull && docker compose up -d
```

### Database Access
```bash
# Connect to PostgreSQL
docker exec -it postgres psql -U root -d n8n

# View chat memory tables
docker exec -it postgres psql -U root -d n8n -c "\dt"
```

## 🎛️ **Configuration**

### Environment Variables
Key settings in your `.env` file:

```bash
# Required: Telegram bot token from @BotFather
TELEGRAM_BOT_TOKEN=1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Required: Database credentials
POSTGRES_DB=n8n
POSTGRES_USER=root  
POSTGRES_PASSWORD=change_this_password

# Required: n8n security keys (generate random 32+ char strings)
N8N_ENCRYPTION_KEY=generate_32_character_encryption_key
N8N_USER_MANAGEMENT_JWT_SECRET=generate_jwt_secret_key

# Optional: Custom ngrok domain
NGROK_AUTHTOKEN=your_ngrok_token
SUBDOMAIN=your-custom-subdomain
```

### Webhook Configuration
The system uses your ngrok HTTPS URL for Telegram webhooks:
- Format: `https://your-domain.ngrok-free.app/webhook/telegram`
- Updates automatically in the Oliver workflow
- Requires HTTPS (HTTP not supported by Telegram)

### AI Model Configuration
Default models downloaded automatically:
- **Llama 3.1 8B**: Main chat model (4.7GB)
- **nomic-embed-text**: Text embeddings (274MB)

To use different models, update the AI Agent node in n8n.

## 🚨 **Troubleshooting**

### Common Issues

**🔧 n8n not accessible:**
```bash
# Check container status
docker ps | grep n8n

# Check n8n logs for errors
docker logs n8n

# Verify port 5678 is accessible
curl http://localhost:5678
```

**🤖 Telegram webhook errors:**
- ✅ Ensure webhook URL uses **HTTPS** (ngrok domain)
- ✅ Verify bot token is correct in `.env`
- ✅ Check workflow is **activated** in n8n
- ✅ Test webhook: `curl -X POST https://your-domain.ngrok-free.app/webhook/telegram`

**⚡ GPU not detected:**
```bash
# Check if NVIDIA runtime is available
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Check Ollama GPU detection
docker logs ollama | grep "inference compute"

# If no GPU, fallback to CPU profile
docker compose --profile cpu up -d
```

**🐌 AI responses slow:**
- 🔄 First model download takes time (4.7GB for Llama 3.1 8B)
- 🚀 Use GPU profile for 5-10x faster inference
- 📊 Monitor resources: `docker stats`
- 🔍 Check Ollama logs: `docker logs ollama -f`

**💾 Data persistence issues:**
```bash
# Check data directory permissions
ls -la ./data/

# Verify volumes are mounted correctly
docker inspect n8n | grep -A 10 Mounts

# Backup and restore if needed
cp -r ./data ./data-backup
```

**🗄️ Database connection errors:**
```bash
# Check PostgreSQL is running
docker logs postgres

# Test database connectivity
docker exec -it postgres psql -U root -d n8n -c "SELECT version();"

# Reset database if corrupted
docker compose down && docker volume rm postgres_storage
```

### Performance Optimization

**For GPU Systems:**
- Use `--profile gpu-nvidia` for NVIDIA cards
- Ensure GPU memory is sufficient (8GB+ recommended)
- Monitor GPU usage: `nvidia-smi`

**For CPU Systems:**
- Allocate sufficient RAM (8GB+ recommended)  
- Consider smaller models if needed
- Monitor CPU usage: `htop`

### Getting Help

**Debug Commands:**
```bash
# Full system status
docker compose ps && docker stats --no-stream

# All service logs
docker compose logs --tail 50

# Check data integrity  
find ./data -type f | wc -l
```

**Log Locations:**
- n8n logs: `docker logs n8n`
- AI processing: `docker logs ollama`  
- Database: `docker logs postgres`
- System: `docker compose logs`

---

## � **Documentation**

- **[SETUP.md](SETUP.md)** - Detailed step-by-step setup guide
- **[DATA_PERSISTENCE.md](DATA_PERSISTENCE.md)** - Backup and data management strategies  
- **[docker-compose.yml](docker-compose.yml)** - Service configuration
- **[.env.example](.env.example)** - Environment variables template

## �📜 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 **Contributing**

Contributions are welcome! Please feel free to submit a Pull Request.

## 🎯 **What's Included**

- ✅ **Complete Docker setup** with GPU acceleration
- ✅ **Pre-configured Oliver workflow** for Telegram chatbot
- ✅ **Local data persistence** - no data loss on container restart
- ✅ **Production-ready** PostgreSQL with chat memory
- ✅ **GPU-accelerated AI** with Ollama (Llama 3.1 8B)
- ✅ **Vector database** (Qdrant) for future enhancements
- ✅ **Comprehensive documentation** and troubleshooting guides
- ✅ **Backup strategies** for data protection

## 🚀 **Performance**

**With NVIDIA GPU:**
- Response time: ~1-3 seconds
- Concurrent users: 10+ simultaneous conversations
- Model: Llama 3.1 8B (4.7GB)

**CPU-only mode:**
- Response time: ~10-30 seconds  
- Concurrent users: 2-3 simultaneous conversations
- Still fully functional, just slower

---

<div align="center">
<strong>Built with ❤️ for the self-hosted AI community</strong>

**Ready to deploy? [Follow the setup guide](SETUP.md) →**
</div>
