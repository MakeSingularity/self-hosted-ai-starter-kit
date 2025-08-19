# GitHub Copilot Integration Guide

This project is configured for optimal GitHub Copilot integration with project-specific context.

## Project-Specific Context Configuration

### Method 1: `.copilot/instructions.md` (Recommended)

The project includes a `.copilot/instructions.md` file that provides GitHub Copilot with project-specific context:

- Primary architecture reference: `PROJECT_INSTRUCTIONS.yaml`
- Key tech stack and development standards
- AI agent communication patterns
- Hardware and security specifications

### Method 2: `.copilotinclude` File

The `.copilotinclude` file controls which files are included in Copilot's context:

- **Includes**: PROJECT_INSTRUCTIONS.yaml, documentation files
- **Excludes**: Data files, logs, runtime artifacts that would clutter context

### Method 3: Workspace Settings

VS Code workspace settings (`.vscode/settings.json`) include:

- File associations for YAML and project-specific files
- Enhanced editor configuration for this project
- Python environment configuration

## How This Maintains Project Isolation

1. **Local Configuration**: All Copilot settings are workspace-specific
2. **File Filtering**: `.copilotinclude` ensures only relevant files provide context
3. **Project Instructions**: The `.copilot/instructions.md` file is only active in this workspace
4. **No Global Impact**: Other projects remain unaffected by these configurations

## Using Copilot with This Project

1. **Architecture Questions**: Ask about modular design, AI agent patterns
2. **Implementation**: Request code that follows the PROJECT_INSTRUCTIONS.yaml
3. **Zone Intelligence**: Get help with camera zone configurations
4. **n8n Workflows**: Assistance with workflow automation patterns

## Key Context Files for Copilot

- `PROJECT_INSTRUCTIONS.yaml` - Master architecture document
- `.copilot/instructions.md` - Copilot-specific guidance
- `docs/` - Implementation guides and setup documentation
- `shared/system_metrics.py` - Core monitoring utilities

This setup ensures GitHub Copilot understands the project's modular, neural network-inspired architecture while keeping other projects isolated from this context.
