# 💾 Data Persistence & Backup Guide

This guide explains how data persistence works in the AI Telegram chatbot and provides backup strategies.

## 🏗️ Data Architecture

### Local Data Structure
All container data is persisted locally in the `./data/` directory:

```
data/
├── n8n/                    # n8n workflow engine data
│   ├── config             # n8n configuration files
│   ├── nodes/             # Custom nodes and packages
│   ├── binaryData/        # File uploads and attachments
│   │   └── workflows/     # Workflow binary data
│   └── ...               # Logs, cache, settings
│
├── postgres/              # PostgreSQL database files  
│   ├── base/             # Database tables and indexes
│   ├── global/           # Global database settings
│   ├── pg_wal/           # Write-ahead log files
│   └── ...              # System catalogs, configs
│
├── ollama/               # AI model storage
│   ├── models/           # Downloaded AI models
│   │   ├── blobs/        # Model binary data (4.7GB+)
│   │   └── manifests/    # Model metadata
│   └── ...              # Cache, logs
│
└── qdrant/               # Vector database storage
    ├── collection/       # Vector collections
    ├── snapshots/        # Database snapshots
    └── ...              # Indexes, metadata
```

### Volume Mappings
The `docker-compose.yml` maps container paths to local directories:

```yaml
services:
  n8n:
    volumes:
      - ./data/n8n:/home/node/.n8n
      
  postgres:
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
      
  ollama:
    volumes:
      - ./data/ollama:/root/.ollama
      
  qdrant:
    volumes:
      - ./data/qdrant:/qdrant/storage
```

## 💾 Backup Strategies

### Simple Backup (Recommended)
```bash
# Create timestamped backup
cp -r ./data ./backup-$(date +%Y%m%d-%H%M%S)

# Include environment configuration
cp .env ./backup-$(date +%Y%m%d-%H%M%S)/
```

### Compressed Backup
```bash
# Create compressed backup (saves space)
tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz ./data .env

# List backup contents
tar -tzf backup-YYYYMMDD-HHMMSS.tar.gz

# Extract backup
tar -xzf backup-YYYYMMDD-HHMMSS.tar.gz
```

### Automated Backup Script
Create `backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="ai-chatbot-backup-$DATE"

# Create backup directory
mkdir -p $BACKUP_DIR

# Stop containers for consistent backup
echo "Stopping containers..."
docker compose down

# Create backup
echo "Creating backup: $BACKUP_NAME"
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" ./data .env

# Restart containers
echo "Restarting containers..."
docker compose --profile gpu-nvidia up -d

echo "Backup completed: $BACKUP_DIR/$BACKUP_NAME.tar.gz"

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

Make executable and run:
```bash
chmod +x backup.sh
./backup.sh
```

### Live Backup (Hot Backup)
For continuous operation without downtime:
```bash
# Create live backup while containers are running
mkdir -p ./live-backup-$(date +%Y%m%d)

# Copy data with rsync (preserves permissions)
rsync -av --progress ./data/ ./live-backup-$(date +%Y%m%d)/data/
cp .env ./live-backup-$(date +%Y%m%d)/
```

## 🔄 Restore Procedures

### Complete Restore
```bash
# Stop all containers
docker compose down

# Remove current data (⚠️ WARNING: This deletes current data)
rm -rf ./data

# Extract backup
tar -xzf backup-YYYYMMDD-HHMMSS.tar.gz

# Restore environment
cp backup-YYYYMMDD-HHMMSS/.env .env

# Restart containers
docker compose --profile gpu-nvidia up -d
```

### Selective Restore
Restore specific components:

```bash
# Stop specific service
docker compose stop n8n

# Restore only n8n data
rm -rf ./data/n8n
tar -xzf backup-YYYYMMDD-HHMMSS.tar.gz data/n8n
mv data/n8n ./data/

# Restart service
docker compose start n8n
```

### Database-Only Restore
```bash
# Stop database
docker compose stop postgres

# Restore PostgreSQL data
rm -rf ./data/postgres
tar -xzf backup-YYYYMMDD-HHMMSS.tar.gz data/postgres
mv data/postgres ./data/

# Restart database and dependent services
docker compose start postgres
docker compose start n8n
```

## 📊 Data Size Management

### Check Data Usage
```bash
# Overall data usage
du -sh ./data

# Per-service breakdown
du -sh ./data/*

# Detailed analysis
find ./data -type f -size +100M -exec ls -lh {} \;
```

### Model Storage Optimization
Ollama models can be large (4.7GB+ each):

```bash
# List installed models
docker exec ollama ollama list

# Remove unused models
docker exec ollama ollama rm model_name

# Check model sizes
docker exec ollama find /root/.ollama -name "*.bin" -exec ls -lh {} \;
```

### Clean Up Strategies
```bash
# Clean n8n logs (if too large)
docker exec n8n find /home/node/.n8n/logs -name "*.log" -mtime +30 -delete

# Clean PostgreSQL old WAL files (handled automatically)
docker exec postgres pg_archivecleanup /var/lib/postgresql/data/pg_wal 000000010000000000000010

# Docker cleanup (removes unused images/containers)
docker system prune -f
```

## 🔐 Security Considerations

### Backup Security
```bash
# Encrypt sensitive backups
gpg --symmetric --cipher-algo AES256 backup-YYYYMMDD.tar.gz

# Decrypt when needed
gpg --decrypt backup-YYYYMMDD.tar.gz.gpg > backup-YYYYMMDD.tar.gz
```

### Environment File Protection
```bash
# The .env file contains sensitive tokens
chmod 600 .env

# Include .env in .gitignore
echo ".env" >> .gitignore

# Backup .env separately and securely
gpg --symmetric .env
```

### Access Control
```bash
# Restrict data directory permissions
chmod 750 ./data
chmod -R 640 ./data/*

# Create backup user (Linux)
sudo useradd -r -s /bin/false backup-user
sudo chown -R backup-user:backup-user ./backups
```

## 📋 Backup Checklist

### Daily Backup
- [ ] Automated script runs successfully
- [ ] Backup size is reasonable (check for growth)
- [ ] Old backups are cleaned up
- [ ] Services remain operational

### Weekly Verification
- [ ] Test restore procedure with recent backup
- [ ] Verify backup integrity (file checksums)
- [ ] Check available disk space
- [ ] Review backup retention policy

### Monthly Maintenance
- [ ] Full backup to external storage
- [ ] Clean up unnecessary model files
- [ ] Update backup procedures if needed
- [ ] Test disaster recovery plan

## 🚨 Disaster Recovery

### Quick Recovery Commands
```bash
# Emergency restore (latest backup)
docker compose down
tar -xzf $(ls -t backups/*.tar.gz | head -1)
docker compose --profile gpu-nvidia up -d
```

### Data Corruption Recovery
```bash
# If PostgreSQL is corrupted
docker compose stop postgres
rm -rf ./data/postgres
# Restore from backup or reinitialize
```

### Migration to New System
1. Create backup on old system
2. Transfer backup file to new system
3. Install Docker and clone repository
4. Extract backup and configure environment
5. Start services with restored data

## 📈 Monitoring & Alerts

### Backup Monitoring
```bash
# Check backup freshness
find ./backups -name "*.tar.gz" -mtime -1

# Monitor data growth
watch -n 60 'du -sh ./data'

# Alert on large files
find ./data -size +1G -exec echo "Large file: {}" \;
```

### Automated Alerts
Set up monitoring for:
- Backup job failures
- Rapid data growth
- Disk space warnings
- Container health issues

This persistence strategy ensures your AI chatbot data survives container recreation, system updates, and hardware migrations while maintaining performance and security.
