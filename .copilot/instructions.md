# GitHub Copilot Project Context

This is the **Self-Hosted AI Starter Kit** project for building an intelligent workshop assistant.

## Key Context Files

- `PROJECT_INSTRUCTIONS.yaml` - Complete project architecture and design bible
- `docs/N8N_NODE_SETUP_GUIDE.md` - n8n workflow configurations
- `scripts/whisper_service_manager.py` - Service management utilities

## Project Focus

- **Current Phase**: Voice integration and workflow automation via n8n
- **Future Vision**: Multi-modal workshop assistant with vision, audio, and zone-based intelligence
- **Architecture**: Neural network-inspired modular AI system

## AI Agent Guidelines

When working on this project, always reference `PROJECT_INSTRUCTIONS.yaml` for:

- Modular architecture patterns
- Zone-specific configurations (Oliver-1,2,3,4 cameras)
- AI agent communication protocols
- Hardware specifications (OLIVER server with RTX 4080 SUPER)
- Security model (isolated IoT network, local-only processing)

## Current Tech Stack

- **Workflow**: n8n for orchestration
- **AI**: Ollama (llama3.1:latest) + Whisper API
- **Vision**: 4x Vimtag 847 PTZ cameras
- **Storage**: PostgreSQL + Qdrant vector DB
- **Platform**: Docker on Windows 11 Pro

## Development Standards

- Use `.venv` virtual environment for Python
- Follow modular architecture principles
- Maintain local-only data processing
- Implement AI-agent-to-AI-agent communication patterns
