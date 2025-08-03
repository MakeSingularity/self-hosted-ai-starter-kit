# 🚨 Troubleshooting Guide

## Common Issues and Quick Fixes

### 🐍 Python Import Errors

**Problem**: `ImportError: No module named 'fastapi'`
```bash
❌ ImportError: No module named 'fastapi'
```

**Solutions**:
1. **Quick Fix**: Run setup verification
   ```bash
   python verify_setup.py
   ```

2. **Manual Fix**: Install core packages
   ```bash
   pip install fastapi uvicorn pydantic python-dotenv requests
   ```

3. **Full Fix**: Install all requirements
   ```bash
   pip install -r requirements.txt
   ```

---

### 🐳 Docker Issues

**Problem**: `docker: command not found`
```bash
❌ 'docker' is not recognized as an internal or external command
```

**Solution**: Install Docker Desktop
1. Download: [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Install and restart your computer
3. Verify: `docker --version`

**Problem**: Docker containers won't start
```bash
❌ Error response from daemon: driver failed programming external connectivity
```

**Solutions**:
1. Check if ports are in use:
   ```bash
   # Windows
   netstat -ano | findstr :5678
   netstat -ano | findstr :8000
   
   # Stop conflicting processes or change ports in docker-compose.yml
   ```

2. Restart Docker Desktop
3. Try different ports in `.env` file

---

### 🎤 Speech Service Issues

**Problem**: NVIDIA Riva not working
```bash
❌ Import "riva.client" could not be resolved
```

**Solution**: Riva is optional! The system works without it.
1. Use local TTS instead: The system automatically falls back to `pyttsx3`
2. To install Riva (optional): `pip install nvidia-riva-client`
3. See `docs/SPEECH_INTEGRATION.md` for full setup

---

### 🔧 Environment Issues

**Problem**: Environment variables not loading
```bash
❌ KeyError: 'SOME_ENV_VAR'
```

**Solution**: Create `.env` file
1. Copy the example: `cp .env.example .env`
2. Edit `.env` with your settings
3. Restart the application

---

### 🚀 Quick Diagnostics

Run these commands to check your setup:

```bash
# 1. Check Python version
python --version

# 2. Check if Docker is running
docker --version

# 3. Verify setup
python verify_setup.py

# 4. Test imports
python -c "import fastapi, uvicorn, pydantic; print('✅ Core packages OK')"

# 5. Check ports
netstat -ano | findstr :5678  # n8n
netstat -ano | findstr :8000  # API server
```

---

### 🆘 Still Having Issues?

1. **Start Fresh**: 
   ```bash
   # Create new virtual environment
   python -m venv fresh_env
   fresh_env\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Minimal Setup**: Start with just the API server
   ```bash
   pip install fastapi uvicorn
   python examples/api_server.py
   ```

3. **Check Documentation**:
   - `README.md` - Main guide
   - `docs/SETUP_GUIDE.md` - Detailed setup
   - `PROJECT_STRUCTURE.md` - File organization

4. **Platform-Specific**:
   - **Windows**: Ensure PowerShell execution policy allows scripts
   - **Mac**: Use `host.docker.internal` for Ollama in Docker
   - **Linux**: Check Docker permissions for your user

---

### 📞 Getting Help

If you're still stuck:
1. Check if your issue is in this guide
2. Review the setup verification output: `python verify_setup.py`
3. Look at the project structure: `PROJECT_STRUCTURE.md`
4. Check Docker logs: `docker-compose logs`

**Remember**: The system is designed to work even if some components are missing. Start with the basics and add features incrementally!
