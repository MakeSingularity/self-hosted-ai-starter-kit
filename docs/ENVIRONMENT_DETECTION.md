# Environment Detection for AI Agents

## Overview

The Environment Detection API provides comprehensive runtime environment analysis to help AI agents adapt their behavior based on available resources, execution context, and system capabilities.

## 🎯 **Use Cases**

### For AI Agents
- **Resource Adaptation**: Adjust model size and batch size based on available memory
- **Processing Strategy**: Choose GPU vs CPU processing based on hardware
- **Service Integration**: Adapt to available services (n8n, Ollama, Qdrant, etc.)
- **Container Awareness**: Modify behavior in containerized vs native environments
- **Network Adaptation**: Switch to local-only mode when internet unavailable

### For n8n Workflows
- **Dynamic Workflow Routing**: Branch logic based on environment capabilities
- **Resource-Aware Processing**: Automatically adjust processing intensity
- **Service Discovery**: Detect and utilize available AI services
- **Error Prevention**: Avoid operations that won't work in current environment

## 🚀 **Quick Start**

### 1. Start the Environment Detection API

```bash
# Start the API server
python examples/environment_detector.py

# API will be available at:
# - Health Check: http://localhost:8002/health
# - Quick Check: http://localhost:8002/quick-check
# - Full Detection: http://localhost:8002/detect-environment
# - Documentation: http://localhost:8002/docs
```

### 2. Basic Usage in n8n

**HTTP Request Node Configuration:**
```json
{
  "method": "GET",
  "url": "http://localhost:8002/quick-check",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

**Response Example:**
```json
{
  "environment_type": "native",
  "memory_gb": 16.0,
  "cpu_count": 8,
  "gpu_available": true,
  "internet_connected": true,
  "services_running": {
    "n8n": true,
    "api_server": true,
    "speech_api": false,
    "ollama": true,
    "qdrant": false,
    "postgres": true
  }
}
```

### 3. AI Agent Adaptation Logic

```javascript
// n8n Code Node Example
const env = $json; // Environment data from API

// Adapt based on memory
let modelSize = 'small';
let batchSize = 8;

if (env.memory_gb >= 16) {
  modelSize = 'large';
  batchSize = 32;
} else if (env.memory_gb >= 8) {
  modelSize = 'medium';
  batchSize = 16;
}

// Adapt based on GPU
if (env.gpu_available) {
  batchSize *= 2; // Can handle larger batches
}

// Adapt based on environment
const strategy = {
  model_size: modelSize,
  batch_size: batchSize,
  use_gpu: env.gpu_available,
  memory_optimization: env.memory_gb < 8,
  local_only: !env.internet_connected,
  container_mode: env.environment_type === 'container'
};

return { json: { strategy } };
```

## 📊 **API Endpoints**

### `/quick-check` - Fast Environment Summary
**Use Case**: Quick decisions in workflows
**Response Time**: ~1 second
**Returns**: Basic environment info for fast branching logic

```json
{
  "environment_type": "native|container",
  "memory_gb": 16.0,
  "cpu_count": 8,
  "gpu_available": true,
  "internet_connected": true,
  "services_running": {...}
}
```

### `/detect-environment` - Comprehensive Analysis
**Use Case**: Detailed environment assessment
**Response Time**: ~3-5 seconds
**Returns**: Complete environment profile

```json
{
  "environment_type": "native",
  "container_info": {...},
  "system_info": {...},
  "hardware_info": {...},
  "software_capabilities": {...},
  "network_info": {...},
  "ai_capabilities": {...},
  "recommendations": [...]
}
```

### `/ai-capabilities` - AI-Specific Assessment
**Use Case**: AI framework and model compatibility
**Returns**: AI-specific capabilities and recommendations

```json
{
  "llm_support": true,
  "gpu_acceleration": true,
  "speech_synthesis": true,
  "speech_recognition": true,
  "vector_database": true,
  "recommended_config": {...}
}
```

### `/recommendations` - Environment-Based Guidance
**Use Case**: Get actionable recommendations
**Returns**: List of environment-specific recommendations

```json
{
  "recommendations": [
    "✅ Sufficient memory for large AI models.",
    "🚀 GPU detected. Enable GPU acceleration for faster AI processing.",
    "✅ n8n is running and accessible."
  ],
  "summary": {
    "memory_status": "sufficient",
    "gpu_status": "available", 
    "ai_ready": true
  }
}
```

## 🧠 **AI Agent Patterns**

### 1. Resource-Adaptive Processing

```javascript
// Get environment info
const env = await $httpRequest({
  url: 'http://localhost:8002/quick-check'
});

// Adapt processing strategy
if (env.memory_gb < 4) {
  // Ultra-lightweight processing
  return processWithTinyModel(input);
} else if (env.memory_gb < 8) {
  // Moderate processing
  return processWithSmallModel(input);
} else {
  // Full processing power
  return processWithLargeModel(input);
}
```

### 2. Service-Aware Workflows

```javascript
const env = await $httpRequest({
  url: 'http://localhost:8002/quick-check'
});

// Route based on available services
if (env.services_running.ollama) {
  // Use local LLM
  return callOllama(prompt);
} else if (env.internet_connected) {
  // Use cloud API
  return callOpenAI(prompt);
} else {
  // Fallback to simple processing
  return basicTextProcessing(prompt);
}
```

### 3. Container-Aware Operations

```javascript
const env = await $httpRequest({
  url: 'http://localhost:8002/quick-check'
});

if (env.environment_type === 'container') {
  // Conservative resource usage
  const config = {
    batch_size: 8,
    memory_limit: '2gb',
    timeout: 30000
  };
} else {
  // Can use more resources
  const config = {
    batch_size: 32,
    memory_limit: '8gb',
    timeout: 120000
  };
}
```

## 🔧 **n8n Workflow Templates**

### Environment-Aware AI Agent
**File**: `n8n/demo-data/workflows/environment-aware-ai-agent.json`

This workflow demonstrates:
1. Environment detection
2. Branching logic based on environment type
3. Adaptive AI processing
4. Context creation for other workflows

**Import Steps**:
1. Open n8n: http://localhost:5678
2. Go to Workflows → Import
3. Load the JSON file
4. Configure HTTP request URLs if needed

### Key Workflow Features:
- **Environment Detection**: Automatic runtime analysis
- **Branching Logic**: Different paths for container vs native
- **Resource Adaptation**: Adjust processing based on available resources
- **Context Generation**: Create environment context for other workflows

## 🎛️ **Configuration**

### Environment Variables
```bash
# .env configuration
ENVIRONMENT_API_PORT=8002
API_PORT=8000
SPEECH_API_PORT=8001
```

### Custom Detection Rules
Modify `examples/environment_detector.py` to add custom detection logic:

```python
def custom_environment_check(self) -> Dict[str, Any]:
    """Add your custom environment detection logic"""
    return {
        "custom_service": self.check_custom_service(),
        "special_hardware": self.detect_special_hardware(),
        "organization_config": self.get_org_config()
    }
```

## 🔍 **Testing**

### Manual Testing
```bash
# Test the API directly
curl http://localhost:8002/quick-check

# Run comprehensive test
python tests/test_environment_detection.py
```

### Integration Testing
```bash
# Start all services
docker-compose up -d
python examples/environment_detector.py

# Test in n8n
# Import environment-aware-ai-agent.json workflow
# Execute and observe adaptive behavior
```

## 💡 **Best Practices**

### 1. Cache Environment Data
- Environment rarely changes during execution
- Cache results for 5-10 minutes to avoid repeated API calls
- Use n8n's global data or workflow variables

### 2. Graceful Degradation
- Always provide fallback options when services unavailable
- Test workflows with different environment configurations
- Use try-catch blocks around environment-dependent operations

### 3. Resource Monitoring
- Monitor actual resource usage vs detected capabilities
- Adjust detection thresholds based on real-world performance
- Log environment decisions for debugging

### 4. Security Considerations
- Environment API exposes system information
- Run on localhost only unless explicitly needed
- Filter sensitive environment variables

## 🚀 **Advanced Use Cases**

### Dynamic Model Selection
```javascript
const capabilities = await $httpRequest({
  url: 'http://localhost:8002/ai-capabilities'
});

let modelEndpoint;
if (capabilities.gpu_acceleration && capabilities.llm_support) {
  modelEndpoint = 'http://localhost:11434/api/generate'; // Ollama
} else if (capabilities.speech_synthesis) {
  modelEndpoint = 'http://localhost:8001/synthesize'; // Speech API
} else {
  modelEndpoint = 'http://localhost:8000/process-text'; // Basic API
}
```

### Auto-Scaling Workflows
```javascript
const env = await $httpRequest({
  url: 'http://localhost:8002/quick-check'
});

// Adjust parallel processing based on resources
const parallelNodes = Math.min(
  env.cpu_count,
  Math.floor(env.memory_gb / 2)
);

// Split workload accordingly
return splitWorkload(data, parallelNodes);
```

### Environment-Specific Error Handling
```javascript
const env = await $httpRequest({
  url: 'http://localhost:8002/quick-check'
});

try {
  return await processData(input);
} catch (error) {
  if (env.environment_type === 'container') {
    // Container-specific error handling
    return handleContainerError(error);
  } else {
    // Native environment error handling
    return handleNativeError(error);
  }
}
```

This environment detection system provides the foundation for truly adaptive AI agents that can intelligently respond to their execution context and available resources.
