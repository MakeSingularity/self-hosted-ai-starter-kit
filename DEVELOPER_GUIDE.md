# 🚀 Developer Onboarding Guide

## ⚡ Quick Start
1. **Clone & Open**: `git clone <repo-url> && cd self-hosted-ai-starter-kit && code .`
2. **Setup Environment**: Use VS Code's built-in terminal and run the "Full Development Setup" task
3. **Start Developing**: All tools and integrations are pre-configured!

## 🎮 **GPU-Accelerated Setup**
**IMPORTANT**: This project uses **NVIDIA GPU acceleration**. All Docker Compose commands use the `gpu-nvidia` profile:
```bash
docker compose --profile gpu-nvidia up -d    # ✅ Correct
docker compose up -d                         # ❌ Wrong (CPU only)
```

## 🔧 VS Code Setup (Pre-configured)

### **Tasks Available** (Ctrl+Shift+P → "Tasks: Run Task")
- 🚀 **n8n: Full Development Setup** - Complete setup (start services + sync workflows)
- 🔄 **n8n: Sync Workflows to Workspace** - Refresh workflow status
- 💾 **n8n: Backup All Workflows** - Version control backup
- ▶️ **n8n: Start All Services** - Start Docker containers
- ⏹️ **n8n: Stop All Services** - Stop Docker containers
- 📋 **n8n: View Service Logs** - Monitor n8n logs
- 🌐 **n8n: Open Web Interface** - Open n8n in browser

### **Keyboard Shortcuts** (All start with Ctrl+Shift+N)
- `Ctrl+Shift+N + Ctrl+Shift+F` - Full Development Setup
- `Ctrl+Shift+N + Ctrl+Shift+S` - Sync Workflows
- `Ctrl+Shift+N + Ctrl+Shift+B` - Backup Workflows
- `Ctrl+Shift+N + Ctrl+Shift+O` - Open n8n Web Interface
- `Ctrl+Shift+N + Ctrl+Shift+U` - Start Services
- `Ctrl+Shift+N + Ctrl+Shift+D` - Stop Services
- `Ctrl+Shift+N + Ctrl+Shift+L` - View Logs

## 📁 Workspace Structure
- `workflows_live/` - Live n8n status and reports (auto-updated)
- `workflows_backup/` - Version-controlled workflow files
- `scripts/` - Integration and automation scripts
- `.vscode/` - Pre-configured VS Code settings

## 🤖 Copilot Integration

### **The Copilot Tool** 
GitHub Copilot has access to a specialized n8n tool that can:
- Monitor workflow status in real-time
- Analyze workflow performance and complexity
- Provide optimization recommendations
- Backup workflows for version control
- Generate development insights

### **How Copilot Uses It**
Simply ask Copilot questions like:
- "What's the status of our n8n workflows?"
- "Analyze the Oliver workflow for optimization"
- "Backup all workflows and show me what changed"
- "What are the current health metrics?"

Copilot will automatically use the tool to get real-time information.

## 🔄 Development Workflow

### **Daily Development**
1. Open VS Code: `code .`
2. Run "Full Development Setup" task (Ctrl+Shift+N + Ctrl+Shift+F)
3. Work on n8n workflows in the web interface
4. Sync changes to workspace when needed
5. Commit workflow changes to Git

### **Working with Workflows**
1. **Edit**: Use n8n web interface (http://localhost:5678)
2. **Sync**: Run sync task to update VS Code workspace
3. **Version Control**: Workflow JSON files are in `workflows_backup/`
4. **Monitor**: Live status in `workflows_live/README.md`

### **Collaboration**
- All workflow changes are tracked in Git
- Team members can see workflow structure without running n8n
- Copilot can analyze workflows for any team member
- Documentation is auto-generated and kept up-to-date

## 🔧 Configuration

### **API Token Management**
The n8n API token is stored in `.vscode/settings.json`. To update:
1. Generate new token in n8n web interface (Settings → API Keys)
2. Update `n8n.apiKey` in `.vscode/settings.json`
3. Restart VS Code or reload the window

### **Customization**
- Modify tasks in `.vscode/tasks.json`
- Adjust keybindings in `.vscode/keybindings.json`
- Configure workspace settings in `.vscode/settings.json`

## 🚨 Troubleshooting

### **Services Not Starting**
```bash
docker compose down
docker compose up -d
```

### **API Connection Issues**
1. Check if n8n is running: http://localhost:5678
2. Verify API token in settings
3. Check Docker containers: `docker compose ps`

### **Sync Issues**
1. Run "Sync Workflows" task manually
2. Check `workflows_live/` for error messages
3. Verify n8n instance is accessible

## 📚 Additional Resources
- [n8n Documentation](https://docs.n8n.io/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [VS Code Tasks Documentation](https://code.visualstudio.com/docs/editor/tasks)

---
*This workspace is optimized for seamless n8n development with GitHub Copilot integration.*
