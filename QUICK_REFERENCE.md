# 🚀 Quick Reference - AI Telegram Chatbot

Essential commands and information for daily operation.

## ⚡ Quick Start Commands

```bash
# Clone and setup
git clone https://github.com/MakeSingularity/self-hosted-ai-starter-kit.git
cd self-hosted-ai-starter-kit
cp .env.example .env

# Create data directories
mkdir -p data/{n8n,postgres,ollama,qdrant}

# Start with GPU (recommended)
docker compose --profile gpu-nvidia up -d

# Start with CPU only
docker compose --profile cpu up -d

# Stop all services
docker compose down
```

## 📊 Status & Monitoring

```bash
# Check all containers
docker compose ps

# Check GPU detection
docker logs ollama | grep "inference compute"

# Monitor resources
docker stats --no-stream

# View logs
docker logs n8n -f          # n8n workflow logs
docker logs ollama -f       # AI processing logs
docker logs postgres        # Database logs
```

## 🔧 Service Management

```bash
# Restart specific service
docker restart n8n
docker restart ollama
docker restart postgres

# Update containers
docker compose pull
docker compose up -d

# View service URLs
echo "n8n: http://localhost:5678"
echo "Ollama: http://localhost:11434"
echo "Qdrant: http://localhost:6333"
```

## 💾 Backup Commands

```bash
# Quick backup
cp -r ./data ./backup-$(date +%Y%m%d)

# Compressed backup
tar -czf backup-$(date +%Y%m%d).tar.gz ./data .env

# Restore from backup
docker compose down
tar -xzf backup-YYYYMMDD.tar.gz
docker compose --profile gpu-nvidia up -d
```

## 🛠️ Troubleshooting

```bash
# Reset everything (⚠️ DELETES DATA)
docker compose down -v
rm -rf ./data
mkdir -p data/{n8n,postgres,ollama,qdrant}
docker compose --profile gpu-nvidia up -d

# Check n8n accessibility
curl -s -w "%{http_code}" http://localhost:5678

# Test Ollama API
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "prompt": "Hello", "stream": false}'

# Database connection test
docker exec -it postgres psql -U root -d n8n -c "SELECT version();"
```

## 📱 Telegram Bot Setup

1. **Create bot**: Message [@BotFather](https://t.me/botfather) → `/newbot`
2. **Get token**: Copy token from BotFather
3. **Update .env**: Set `TELEGRAM_BOT_TOKEN=your_token`
4. **Setup ngrok**: Point to `localhost:5678`, get HTTPS URL
5. **Configure n8n**: Update webhook URL in Telegram Trigger node
6. **Test**: Send message to your bot

## 🔍 Important Files

```bash
.env                    # Your configuration (keep secure!)
docker-compose.yml      # Service definitions
data/                   # All persistent data
├── n8n/               # Workflows, credentials
├── postgres/          # Chat history, database
├── ollama/            # AI models (4.7GB+)
└── qdrant/            # Vector storage
```

## 🎯 Service Endpoints

| Service | Internal | External | Purpose |
|---------|----------|----------|---------|
| n8n | http://n8n:5678 | http://localhost:5678 | Workflow editor |
| Ollama | http://ollama:11434 | http://localhost:11434 | AI inference |
| PostgreSQL | postgres:5432 | localhost:5432 | Database |
| Qdrant | http://qdrant:6333 | http://localhost:6333 | Vector DB |

## 🚨 Emergency Commands

```bash
# Service not responding
docker restart SERVICE_NAME

# High memory usage
docker stats
docker system prune -f

# Corrupt database
docker compose stop postgres
rm -rf ./data/postgres
# Restore from backup

# Lost ngrok URL
# Get new URL from ngrok, update Telegram Trigger node

# Telegram webhook broken
# Check HTTPS URL, verify bot token, reactivate workflow
```

## 📋 Health Checks

```bash
# All services running?
docker compose ps | grep -c "Up"  # Should show 4

# Disk space sufficient?
df -h | grep -E "/$|data"

# Models downloaded?
docker exec ollama ollama list

# Workflow active?
curl http://localhost:5678/rest/active-workflows
```

## 💡 Tips

- **Keep .env secure** - Contains sensitive tokens
- **Regular backups** - Data is precious
- **Monitor disk space** - AI models are large
- **Use HTTPS** - Telegram requires it for webhooks
- **GPU preferred** - 5-10x faster than CPU
- **Update regularly** - Pull latest Docker images

## 🔗 Quick Links

- [Setup Guide](SETUP.md)
- [Data Persistence](DATA_PERSISTENCE.md)
- [Main README](README.md)
- [n8n Documentation](https://docs.n8n.io/)
- [Ollama Models](https://ollama.ai/library)

---
**Need help?** Check logs first: `docker compose logs --tail 50`
