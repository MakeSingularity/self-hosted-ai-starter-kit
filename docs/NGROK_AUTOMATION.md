# Ngrok Automation for n8n Development

## Overview

The ngrok automation system automatically manages webhook URLs and tunnels for n8n development, solving the issue where Docker Desktop's ngrok extension conflicts with container restarts.

## Features

- **Automatic Tunnel Management**: Creates and manages ngrok tunnels with your reserved domain
- **Webhook Auto-Configuration**: Automatically updates webhook URLs in active workflows
- **Conflict Resolution**: Cleans up conflicting ngrok processes from Docker Desktop
- **VS Code Integration**: Full integration with tasks and keyboard shortcuts

## Quick Start

### 1. Basic Setup
```bash
# Using VS Code task (recommended)
Ctrl+Shift+N, Ctrl+Shift+G

# Or via command line
python scripts/ngrok_webhook_manager.py setup
```

### 2. Check Status
```bash
# Using VS Code task
Ctrl+Shift+N, Ctrl+Shift+T

# Or via command line
python scripts/ngrok_webhook_manager.py status
```

### 3. Clean Up Conflicts
```bash
# Using VS Code task
Ctrl+Shift+N, Ctrl+Shift+C

# Or via command line
python scripts/ngrok_webhook_manager.py cleanup
```

## VS Code Integration

### Tasks Available
- **n8n: Setup Ngrok & Webhooks** - Main setup command
- **n8n: Check Ngrok Status** - Status monitoring
- **n8n: Cleanup Ngrok** - Conflict resolution
- **n8n: Full Development Setup** - Complete environment setup

### Keyboard Shortcuts
- `Ctrl+Shift+N, Ctrl+Shift+G` - Setup ngrok & webhooks
- `Ctrl+Shift+N, Ctrl+Shift+T` - Check tunnel status
- `Ctrl+Shift+N, Ctrl+Shift+C` - Cleanup conflicts
- `Ctrl+Shift+N, Ctrl+Shift+F` - Full development setup

## Configuration

### VS Code Settings
```json
{
    "n8n.ngrok.reservedDomain": "mutual-platypus-notable.ngrok-free.app",
    "n8n.ngrok.authToken": "",
    "n8n.webhookAutoSetup": true
}
```

### Environment Variables
```bash
# Optional: Set ngrok auth token
NGROK_AUTHTOKEN=your_token_here

# Optional: Override reserved domain
NGROK_DOMAIN=your-domain.ngrok-free.app
```

## How It Works

### 1. Tunnel Management
- Scans for existing ngrok processes
- Terminates conflicting Docker Desktop ngrok instances
- Creates new tunnel with reserved domain
- Validates tunnel connectivity

### 2. Webhook Configuration
- Retrieves all active workflows from n8n
- Identifies webhook nodes requiring external URLs
- Updates webhook URLs with new ngrok tunnel
- Validates webhook accessibility

### 3. Workflow Integration
- Automatically runs during "Full Development Setup"
- Can be triggered independently
- Provides detailed status reporting
- Handles errors gracefully

## Troubleshooting

### Common Issues

**"Port 4040 already in use"**
```bash
# Run cleanup first
python scripts/ngrok_webhook_manager.py cleanup
# Then try setup again
python scripts/ngrok_webhook_manager.py setup
```

**"No active workflows found"**
- Ensure n8n is running (`docker-compose --profile gpu-nvidia up -d`)
- Check n8n API key in VS Code settings
- Verify workflows are active in n8n interface

**"Webhook update failed"**
- Check n8n API connectivity
- Ensure workflow is not currently executing
- Verify webhook node configuration

### Debug Mode
```bash
# Run with verbose output
python scripts/ngrok_webhook_manager.py setup --verbose

# Check detailed status
python scripts/ngrok_webhook_manager.py status --debug
```

## Development Workflow

### Typical Development Session
1. Start containers: `Ctrl+Shift+N, Ctrl+Shift+U`
2. Setup webhooks: `Ctrl+Shift+N, Ctrl+Shift+G`
3. Open n8n interface: `Ctrl+Shift+N, Ctrl+Shift+O`
4. Develop workflows with automatic webhook management

### Container Restart Workflow
1. Stop services: `Ctrl+Shift+N, Ctrl+Shift+D`
2. Start services: `Ctrl+Shift+N, Ctrl+Shift+U`
3. Auto-setup webhooks: `Ctrl+Shift+N, Ctrl+Shift+G`

### Full Reset Workflow
1. Full setup: `Ctrl+Shift+N, Ctrl+Shift+F`
   - Starts all services
   - Configures ngrok tunnels
   - Syncs workflows
   - Ready for development

## Architecture

### Core Components

**NgrokTunnelManager**
- Process management and cleanup
- Tunnel creation and validation
- Status monitoring

**WebhookConfigurator**
- Workflow analysis and webhook detection
- URL updating and validation
- Error handling and rollback

**N8nIntegration**
- API communication with n8n
- Workflow management
- Status reporting

### Configuration Sources
1. VS Code settings (`.vscode/settings.json`)
2. Environment variables
3. Command line arguments
4. Default values

## Security Considerations

- ngrok auth token should be kept secure
- Reserved domain prevents unauthorized tunnel hijacking
- Webhook URLs are validated before updating
- API keys are stored in VS Code settings (local)

## Performance Notes

- Tunnel creation takes 2-5 seconds
- Webhook updates are batched for efficiency
- Status checks are lightweight and fast
- Cleanup operations are thorough but quick

## Future Enhancements

- [ ] Multiple domain support
- [ ] Webhook URL history tracking
- [ ] Integration with VS Code extension
- [ ] Automated testing framework
- [ ] Performance metrics collection
