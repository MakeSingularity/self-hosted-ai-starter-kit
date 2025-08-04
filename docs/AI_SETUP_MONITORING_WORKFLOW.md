# AI Setup and Monitoring Workflow

## Overview

This comprehensive n8n workflow provides **intelligent setup automation** and **AI-powered service monitoring** for the Self-Hosted AI Starter Kit. It combines environment detection, service health checking, automated setup, and intelligent analysis to ensure your AI platform runs optimally.

## 🚀 Key Features

### 1. **Complete Setup Automation**
- Automatic environment detection and verification
- Docker service health checking
- Intelligent service startup when needed
- Performance scoring and optimization recommendations

### 2. **AI-Powered Analysis**
- Intelligent service status evaluation
- Performance scoring (A-D grades)
- Hardware-aware recommendations
- Context-sensitive insights

### 3. **Comprehensive Monitoring**
- Real-time service health checking
- Continuous monitoring with cron triggers
- Automated report generation
- External system notifications

### 4. **Multi-Format Reports**
- JSON format for programmatic access
- Human-readable text reports
- Performance scoring and grading
- Actionable recommendations

## 📊 Workflow Architecture

```
Manual Trigger → Environment Check → API Health → Docker Status
                                                      ↓
Webhook Notify ← Report Generation ← AI Analysis ← Service Checks
                                                      ↓
                 Auto Setup (if needed) ← Performance Check
```

## 🔧 Node Configuration Details

### Core Nodes:

1. **Manual Setup Trigger**
   - Trigger Type: Manual
   - Purpose: Initiate setup and monitoring on-demand

2. **Check Environment** 
   - Type: Execute Command
   - Command: `python ./run_verify.py`
   - Purpose: Verify Python environment and dependencies

3. **Get Environment Details**
   - Type: HTTP Request
   - URL: `http://localhost:8002/environment`
   - Purpose: Retrieve comprehensive environment information

4. **Service Health Checks** (Multiple nodes)
   - **Check Docker Services**: `docker-compose ps --format json`
   - **Check n8n Health**: `http://localhost:5678/api/v1/workflows`
   - **Check Ollama Models**: `http://localhost:11434/api/tags`
   - **Check Qdrant Collections**: `http://localhost:6333/collections`
   - **Check API Server**: `http://localhost:8000/health`

5. **AI Service Analysis** (JavaScript Code Node)
   - Advanced service analysis and scoring
   - Hardware-aware recommendations
   - Performance grading (A-D scale)
   - Intelligent insights generation

6. **Auto Setup** (Conditional)
   - Type: Execute Command
   - Command: `docker-compose up -d`
   - Triggered when performance score < 70

7. **Report Generation**
   - JSON report: `./shared/ai-setup-status-report.json`
   - Human report: `./shared/ai-setup-status-report.txt`

8. **Continuous Monitoring**
   - Type: Cron Trigger
   - Schedule: Every 15 minutes (`0 */15 * * * *`)

## 🎯 AI Analysis Features

### Performance Scoring (0-100 points):
- **Service Availability (40 points)**: Running services ratio
- **Hardware Score (30 points)**: GPU, RAM, CPU assessment
- **Content Score (30 points)**: Models, workflows, collections

### Intelligent Recommendations:
- **Hardware Optimization**: RAM/GPU upgrade suggestions
- **Service Management**: Missing service identification
- **Content Suggestions**: Model and workflow recommendations
- **Performance Tuning**: Environment-specific optimizations

### Report Grading:
- **A Grade (90-100)**: Excellent - All systems optimal
- **B Grade (80-89)**: Good - Minor optimizations needed
- **C Grade (70-79)**: Satisfactory - Some improvements needed
- **D Grade (<70)**: Needs Improvement - Setup required

## 📋 Setup Instructions

### 1. Import Workflow
```bash
# Copy the workflow file to n8n
cp n8n/demo-data/workflows/ai-setup-and-monitoring-workflow.json /path/to/n8n/workflows/
```

### 2. Required Environment
- Python environment with required packages
- Environment detector API running on port 8002
- Docker and docker-compose available
- All services configured in docker-compose.yml

### 3. File Permissions
Ensure n8n can write to the shared directory:
```bash
chmod 755 ./shared/
```

### 4. Start Environment Detector
```bash
python examples/environment_detector.py
```

## 🔄 Usage Scenarios

### Initial Setup
1. Import workflow into n8n
2. Run manual trigger
3. Review generated reports
4. Follow AI recommendations

### Continuous Monitoring
- Automatic execution every 15 minutes
- Performance tracking over time
- Proactive issue detection
- Automated service recovery

### Development Workflow
- Run before development sessions
- Validate environment health
- Ensure all services are running
- Get optimization recommendations

## 📊 Report Format

### JSON Report Structure:
```json
{
  "timestamp": "2025-08-03T12:00:00.000Z",
  "environment": {
    "type": "Docker Container",
    "hardware": {
      "cpu_cores": 8,
      "memory_gb": 16,
      "gpu_available": true
    }
  },
  "services": {
    "docker_compose": { "status": "running", "health": "healthy" },
    "n8n": { "status": "running", "workflows": 5, "health": "healthy" },
    "ollama": { "status": "running", "models": 3, "health": "healthy" },
    "qdrant": { "status": "running", "collections": 2, "health": "healthy" },
    "api_server": { "status": "running", "health": "healthy" }
  },
  "performance": {
    "score": 95,
    "grade": "A",
    "status": "Excellent"
  },
  "ai_analysis": {
    "insights": ["All services running optimally"],
    "warnings": [],
    "recommendations": ["Consider adding more Ollama models"]
  }
}
```

### Human-Readable Report:
```
🚀 AI STARTER KIT - STATUS REPORT
==================================================

📊 PERFORMANCE SCORE: 95/100 (Grade: A)
Status: Excellent

🖥️  ENVIRONMENT:
Type: Docker Container
CPU Cores: 8
Memory: 16GB
GPU Available: Yes

🔧 SERVICES STATUS:
✅ DOCKER COMPOSE: Running
✅ N8N: Running
✅ OLLAMA: Running
✅ QDRANT: Running
✅ API SERVER: Running

📈 CONTENT SUMMARY:
• Ollama Models: 3
• n8n Workflows: 5
• Qdrant Collections: 2

🤖 AI INSIGHTS:
💡 All services are running! Your AI platform is fully operational.
💡 Ollama has 3 model(s) available

🎯 RECOMMENDATIONS:
🔧 Consider adding more diverse AI models for different use cases

📅 Generated: 8/3/2025, 12:00:00 PM
==================================================
```

## 🔗 Integration Options

### External Notifications
Configure webhook URLs in environment to notify:
- Slack channels
- Discord servers
- Email systems
- Monitoring dashboards

### API Integration
Access reports programmatically:
```bash
# Get latest JSON report
curl http://localhost:8002/reports/latest

# Get performance score
curl http://localhost:8002/performance/score
```

### Custom Triggers
Add additional triggers:
- Webhook triggers for external systems
- File watch triggers for configuration changes
- HTTP request triggers for API calls

## 🚨 Troubleshooting

### Common Issues:

1. **Environment Detector Not Running**
   ```bash
   python examples/environment_detector.py
   ```

2. **File Permission Errors**
   ```bash
   chmod 755 ./shared/
   chown n8n:n8n ./shared/
   ```

3. **Docker Service Issues**
   ```bash
   docker-compose down && docker-compose up -d
   ```

4. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🎛️ Advanced Configuration

### Custom Performance Thresholds
Modify the AI analysis code to adjust scoring:
- Change auto-setup threshold (default: 70)
- Adjust hardware scoring weights
- Customize recommendation logic

### Monitoring Frequency
Adjust cron schedule:
- Every 5 minutes: `0 */5 * * * *`
- Every hour: `0 0 * * * *`
- Daily: `0 0 12 * * *`

### Service Endpoints
Update health check URLs for custom deployments:
- Change port numbers
- Add authentication headers
- Modify timeout values

## 📈 Performance Optimization

### Hardware Recommendations:
- **Minimum**: 8GB RAM, 4 CPU cores
- **Recommended**: 16GB RAM, 8 CPU cores, GPU
- **Optimal**: 32GB RAM, 16 CPU cores, NVIDIA GPU

### Service Optimization:
- Disable unused services to save resources
- Use GPU acceleration for Ollama when available
- Configure Qdrant for your specific use case
- Optimize n8n workflow execution settings

This workflow provides comprehensive setup automation and intelligent monitoring for your AI platform, ensuring optimal performance and proactive issue resolution.
