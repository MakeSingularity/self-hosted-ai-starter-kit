# 🚀 Setup Guide - AI Telegram Chatbot

This guide will help you set up the AI Telegram chatbot from scratch, including GPU acceleration and data persistence.

## ⚡ Quick Start (5 minutes)

### 1. Prerequisites Check
Ensure you have:
- [ ] **Docker Desktop** installed and running
- [ ] **NVIDIA GPU** with drivers (optional but recommended)
- [ ] **ngrok account** (free tier works fine)
- [ ] **Telegram account** for creating a bot

### 2. Create Telegram Bot
1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Choose a name (e.g., "My AI Assistant")
4. Choose a username (e.g., "my_ai_assistant_bot")
5. **Copy the bot token** (looks like `1234567890:ABC-DEF1234ghIkl...`)

### 3. Clone and Configure
```bash
# Clone the repository
git clone https://github.com/MakeSingularity/self-hosted-ai-starter-kit.git
cd self-hosted-ai-starter-kit

# Create environment file
cp .env.example .env
```

### 4. Edit Configuration
Open `.env` file and update:
```bash
# Replace with your bot token from step 2
TELEGRAM_BOT_TOKEN=1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Set secure passwords
POSTGRES_PASSWORD=your_secure_database_password

# Generate encryption keys (32+ characters each)
N8N_ENCRYPTION_KEY=generate_a_32_character_encryption_key
N8N_USER_MANAGEMENT_JWT_SECRET=generate_a_32_character_jwt_secret
```

**💡 Tip:** Generate secure keys with:
```bash
# On Linux/Mac
openssl rand -base64 32

# On Windows PowerShell  
[System.Web.Security.Membership]::GeneratePassword(32, 0)
```

### 5. Start Services
```bash
# Create data directories for persistence
mkdir -p data/{n8n,postgres,ollama,qdrant}

# For NVIDIA GPU (recommended)
docker compose --profile gpu-nvidia up -d

# OR for CPU only
docker compose --profile cpu up -d
```

**Wait 2-3 minutes** for services to start and models to download.

### 6. Setup ngrok Tunnel
**Option A: Docker Desktop Extension (Easiest)**
1. Open Docker Desktop
2. Go to **Extensions** tab
3. Search and install **ngrok extension**
4. Open ngrok extension
5. Create tunnel to `localhost:5678`
6. Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

**Option B: ngrok CLI**
```bash
# Install ngrok and authenticate
ngrok config add-authtoken YOUR_NGROK_TOKEN
ngrok http 5678

# Copy the HTTPS forwarding URL
```

### 7. Configure Workflow
1. Open n8n: `http://localhost:5678` or your ngrok HTTPS URL
2. The **Oliver workflow** should be pre-loaded
3. Click on the **Telegram Trigger** node
4. Update the webhook URL to: `https://your-ngrok-domain.ngrok-free.app`
5. Click **Save** and **Activate** the workflow

### 8. Test Your Bot! 🎉
1. Find your bot on Telegram by username
2. Send a message like "Hello!"
3. Your AI chatbot should respond with GPU-accelerated intelligence!

---

## 🔧 Advanced Configuration

### GPU Verification
Check if GPU is detected:
```bash
docker logs ollama | grep "inference compute"
# Should show: NVIDIA GeForce [Your GPU] total="X.X GiB"
```

### Performance Monitoring
```bash
# Check container status
docker compose ps

# Monitor resource usage
docker stats

# View AI processing logs
docker logs ollama -f
```

### Data Persistence
All data is automatically saved to `./data/`:
- `data/n8n/` - Workflows and settings
- `data/postgres/` - Chat history and database  
- `data/ollama/` - AI models (4.7GB+)
- `data/qdrant/` - Vector database

### Backup Strategy
```bash
# Simple backup
cp -r ./data ./backup-$(date +%Y%m%d)

# Advanced backup with tar
tar -czf backup-$(date +%Y%m%d).tar.gz ./data .env

# Restore from backup
tar -xzf backup-YYYYMMDD.tar.gz
```

---

## 🚨 Troubleshooting

### Common Issues

**❌ "Connection refused" or containers not starting**
```bash
# Check Docker is running
docker version

# Check container logs
docker compose logs

# Restart clean
docker compose down && docker compose --profile gpu-nvidia up -d
```

**❌ GPU not detected**
```bash
# Test NVIDIA Docker support
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# If fails, install nvidia-container-toolkit
# Then restart Docker Desktop
```

**❌ Telegram webhook not working**
- ✅ Ensure webhook URL uses **HTTPS** (not HTTP)
- ✅ Check bot token is correct in `.env`
- ✅ Verify workflow is **activated** in n8n
- ✅ Test URL in browser: should show n8n interface

**❌ AI responses very slow**
- 🔄 First run downloads 4.7GB model (takes time)
- 🚀 Switch to GPU profile: `docker compose --profile gpu-nvidia up -d`
- 📊 Check resources: `docker stats`

**❌ "Permission denied" on data folders**
```bash
# Fix permissions (Linux/Mac)
sudo chown -R $USER:$USER ./data

# Windows: Run Docker Desktop as Administrator
```

### Getting Help

1. **Check logs**: `docker compose logs --tail 50`
2. **Verify config**: Review your `.env` file
3. **Test components**: Try accessing each service individually
4. **Reset if needed**: `docker compose down -v` (⚠️ removes data)

### Support Resources
- [Docker Documentation](https://docs.docker.com/)
- [n8n Documentation](https://docs.n8n.io/)
- [Ollama Documentation](https://ollama.ai/docs)
- [ngrok Documentation](https://ngrok.com/docs)

---

## 🎯 Next Steps

Once your bot is working:

1. **Customize AI personality** - Edit the AI Agent node prompts
2. **Add more models** - Install different Ollama models  
3. **Extend workflows** - Add more n8n automation
4. **Monitor usage** - Set up logging and metrics
5. **Scale up** - Deploy to cloud with persistent storage

Enjoy your self-hosted AI chatbot! 🤖✨
