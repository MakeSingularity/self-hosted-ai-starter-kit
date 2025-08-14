# GitHub Copilot Ngrok Tools Integration

## Overview
This document provides GitHub Copilot with direct access to ngrok automation tools through standardized command patterns.

## Tool Commands Available

### 1. Setup Ngrok and Webhooks
```bash
python scripts/copilot_ngrok_tools.py setup
python scripts/copilot_ngrok_tools.py setup --verbose  # with detailed output
```
**Purpose**: Automatically create ngrok tunnel and configure all webhook URLs
**When to use**: Container restart, initial setup, webhook conflicts

### 2. Check Status
```bash
python scripts/copilot_ngrok_tools.py status
```
**Purpose**: Get current tunnel and webhook status
**When to use**: Debugging, monitoring, before making changes

### 3. Cleanup Conflicts  
```bash
python scripts/copilot_ngrok_tools.py cleanup
```
**Purpose**: Remove conflicting ngrok processes (especially Docker Desktop)
**When to use**: "Port already in use" errors, tunnel conflicts

### 4. Comprehensive Diagnosis
```bash
python scripts/copilot_ngrok_tools.py diagnose
```
**Purpose**: Full analysis with recommendations
**When to use**: Troubleshooting, health checks, unknown issues

### 5. N8N Workflow Status
```bash
python scripts/copilot_ngrok_tools.py n8n-status
```
**Purpose**: Get n8n workflow information and webhook details
**When to use**: Workflow debugging, webhook analysis

## Tool Integration Patterns

### For GitHub Copilot Usage

**When user reports webhook issues:**
1. Run `python scripts/copilot_ngrok_tools.py diagnose`
2. Analyze output and follow recommendations
3. Run specific commands based on diagnosis

**When user mentions container restart:**
1. Run `python scripts/copilot_ngrok_tools.py cleanup`
2. Run `python scripts/copilot_ngrok_tools.py setup`
3. Verify with `python scripts/copilot_ngrok_tools.py status`

**When troubleshooting workflows:**
1. Run `python scripts/copilot_ngrok_tools.py n8n-status`
2. Check for webhook URL mismatches
3. Run setup if webhooks need updating

## Expected Output Formats

All tools return JSON with standardized format:
```json
{
  "success": true/false,
  "output": "detailed output text",
  "error": "error message if any",
  "additional_fields": "specific to command"
}
```

## Common Scenarios

### Scenario 1: User says "webhooks aren't working"
**Response**: Run diagnosis tool first
```bash
python scripts/copilot_ngrok_tools.py diagnose
```

### Scenario 2: User mentions Docker Desktop conflicts
**Response**: Clean up conflicts then setup
```bash
python scripts/copilot_ngrok_tools.py cleanup
python scripts/copilot_ngrok_tools.py setup
```

### Scenario 3: User asks about tunnel status
**Response**: Check current status
```bash
python scripts/copilot_ngrok_tools.py status
```

## Tool Advantages

1. **Direct Integration**: No keyboard shortcuts or UI dependencies
2. **Consistent Output**: JSON format for reliable parsing
3. **Error Handling**: Detailed error information and recommendations
4. **Comprehensive**: Covers all ngrok automation scenarios
5. **Automated**: Minimal user interaction required

## Integration with Existing Tools

These tools complement the existing Copilot n8n tool:
- Use ngrok tools for infrastructure (tunnels, webhooks)
- Use n8n tool for workflow analysis and monitoring
- Both tools work together for complete coverage
