# Oliver AI Agent - Service Status Monitoring

## 📋 **Quick Reference for n8n Read/Write File Nodes**

### 🔍 **Service Status Scripts (Relative Paths)**

| Script | Path | Purpose |
|--------|------|---------|
| **Main Status Checker** | `./verify_setup.py` | Complete system verification |
| **Environment Detection** | `./tests/test_environment_detection.py` | Environment analysis |
| **Speech Services** | `./tests/verify_speech_setup.py` | Speech capabilities check |
| **Quick Start** | `./quick_start.py` | Setup and installation verification |

### 📁 **n8n Read File Node Configuration**

```json
{
  "operation": "read",
  "fileName": "./verify_setup.py",
  "options": {}
}
```

### 📝 **n8n Write File Node Configuration (for Oliver's Reports)**

```json
{
  "operation": "write", 
  "fileName": "./shared/oliver-status-report.txt",
  "data": "={{$json.human_readable_report}}",
  "options": {}
}
```

## 🤖 **Oliver's Service Monitoring Workflow**

### **Workflow File**: `n8n/demo-data/workflows/oliver-service-status-checker.json`

### **What Oliver Does:**

1. **📖 Reads Status Script**: Uses relative path `./verify_setup.py`
2. **🔄 Executes Verification**: Runs the status check
3. **🌐 Checks Environment**: Gets current environment status
4. **🧠 Analyzes Results**: Oliver processes all data intelligently
5. **📊 Generates Report**: Creates human-readable status report
6. **💾 Saves Results**: Stores both JSON and text reports
7. **🤖 AI Summary**: Generates condensed summary

### **Oliver's Analysis Includes:**

- ✅ **Service Health**: Python, Docker, packages, APIs
- 🖥️ **Environment Info**: Memory, CPU, GPU, network
- 💡 **Smart Recommendations**: Actionable next steps
- 🎯 **Overall Status**: Critical/Warning/Healthy

## 📊 **Example Oliver Report**

```text
🤖 Oliver's System Status Report
======================================

Overall Status: HEALTHY

🔍 Service Status:
  ✅ python: healthy
  ✅ docker: healthy  
  ✅ packages: healthy
  🔧 speech services: optional
  ✅ api server: healthy
  ✅ n8n: healthy
  ❌ ollama: stopped

🖥️ Environment:
  Type: native
  Memory: 16 GB
  CPU Cores: 8
  GPU: Available
  Internet: Connected

💡 Recommendations:
  🧠 Ollama not running - start for local LLM support

🎉 All systems operational! Ready for AI workflows.
```

## 🔧 **Using Oliver in Your Workflows**

### **Step 1: Import Oliver's Workflow**
1. Open n8n: `http://localhost:5678`
2. Go to Workflows → Import
3. Select: `n8n/demo-data/workflows/oliver-service-status-checker.json`

### **Step 2: Configure File Paths (Already Set)**
- All paths are relative to project root
- No need to modify paths
- Works across different environments

### **Step 3: Trigger Oliver's Analysis**
```javascript
// In any n8n workflow, trigger Oliver's status check
const triggerResponse = await $httpRequest({
  method: 'POST',
  url: 'http://localhost:5678/webhook/oliver-status',
  body: { 
    check_type: 'full',
    requested_by: 'user_workflow' 
  }
});
```

### **Step 4: Read Oliver's Report**
```json
{
  "operation": "read",
  "fileName": "./shared/oliver-status-report.txt",
  "options": {}
}
```

## 🎯 **Integration Patterns**

### **Before Starting AI Tasks**
```javascript
// Check if system is ready for AI processing
const status = await readFile('./shared/oliver-status-report.json');
const report = JSON.parse(status);

if (report.overall_status === 'healthy') {
  // Proceed with AI task
  return processWithAI(input);
} else {
  // Show Oliver's recommendations
  return { 
    error: 'System not ready',
    recommendations: report.recommendations 
  };
}
```

### **Adaptive Processing Based on Oliver's Analysis**
```javascript
const report = JSON.parse(await readFile('./shared/oliver-status-report.json'));

// Adapt based on Oliver's findings
const config = {
  model_size: report.environment_summary.memory_gb > 8 ? 'large' : 'small',
  use_gpu: report.environment_summary.gpu_available,
  batch_size: report.environment_summary.cpu_count * 2,
  local_only: !report.environment_summary.internet_connected
};
```

### **Health Monitoring Dashboard**
```javascript
// Create a monitoring dashboard using Oliver's data
const healthData = {
  timestamp: new Date().toISOString(),
  services: report.services,
  environment: report.environment_summary,
  recommendations: report.recommendations,
  trend: 'improving' // Track over time
};
```

## 🚀 **Advanced Oliver Features**

### **Scheduled Health Checks**
- Set up cron trigger to run Oliver every 15 minutes
- Automatically alert when status changes
- Track system health trends over time

### **Proactive Monitoring**
- Oliver can detect issues before they become critical
- Predictive recommendations based on resource usage
- Integration with external monitoring tools

### **Multi-Environment Support**
- Same relative paths work in Docker containers
- Automatic adaptation to different deployment environments
- Consistent monitoring across dev/staging/production

## 📁 **File Organization for Oliver**

```
project-root/
├── shared/                    # Oliver's output files
│   ├── oliver-status-report.json    # Detailed JSON report
│   ├── oliver-status-report.txt     # Human-readable report
│   └── oliver-history/              # Historical reports
├── tests/                     # Status checking scripts
│   ├── test_environment_detection.py
│   └── verify_speech_setup.py
├── verify_setup.py           # Main status checker
└── quick_start.py            # Setup verification
```

## 💡 **Pro Tips**

1. **Use Relative Paths**: Always start with `./` for portability
2. **Check Oliver First**: Run status check before complex workflows
3. **Monitor Trends**: Save Oliver's reports with timestamps
4. **Automate Responses**: Use Oliver's recommendations to trigger fixes
5. **Share Reports**: Use `./shared/` folder for cross-workflow communication

Oliver is now ready to be your intelligent system monitor and advisor! 🤖✨
