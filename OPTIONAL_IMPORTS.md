# Optional Example Files - Import Error Handling

The following files are **optional examples** that demonstrate NVIDIA Riva integration. VS Code may show import errors for these files if the optional packages aren't installed - this is normal and expected behavior.

## Files with Optional Dependencies

### Speech/Audio Examples (Optional)
- `examples/riva_integration_example.py` - NVIDIA Riva demo
- `examples/riva_api_server.py` - Riva API server
- `examples/hybrid_speech_api.py` - Multi-engine speech API

### Required vs Optional Packages

**Always Required (Core Functionality):**
- `fastapi` - API framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `python-dotenv` - Environment variables
- `requests` - HTTP client

**Optional (Enhanced Features):**
- `nvidia-riva-client` - NVIDIA Riva speech services
- `soundfile` - Audio file processing
- `edge-tts` - Microsoft Edge TTS
- `librosa` - Audio analysis
- `grpcio` - gRPC communication

## How the System Handles Missing Packages

1. **Graceful Degradation**: Core functionality works without optional packages
2. **Clear Error Messages**: Helpful instructions when packages are missing
3. **Fallback Systems**: Local TTS when cloud services unavailable
4. **Runtime Detection**: Packages checked at runtime, not import time

## Installing Optional Packages

To eliminate VS Code import warnings:

```bash
# Install all packages (including optional)
pip install -r requirements.txt

# Install just speech packages
pip install nvidia-riva-client soundfile edge-tts

# Install just core packages (minimal setup)
pip install fastapi uvicorn pydantic python-dotenv requests
```

## VS Code Import Error Suppression

If you prefer to suppress these warnings in VS Code:

1. Open VS Code settings (Ctrl+,)
2. Search for "python lint"
3. Add to settings.json:
```json
{
    "python.analysis.diagnosticSeverityOverrides": {
        "reportMissingImports": "none"
    }
}
```

Or create a `.vscode/settings.json` file in the project root:
```json
{
    "python.analysis.diagnosticSeverityOverrides": {
        "reportMissingImports": "information"
    }
}
```

**Note**: The project is designed to work perfectly fine with these import "errors" - they indicate optional functionality, not broken code.
