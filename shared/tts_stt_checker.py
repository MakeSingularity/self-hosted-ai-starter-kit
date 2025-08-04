#!/usr/bin/env python3
"""
TTS/STT Readiness Checker for Oliver AI System
Checks availability and readiness of Text-to-Speech and Speech-to-Text models
"""

import json
import sys
import subprocess
import requests
import os
from datetime import datetime

def check_ollama_models():
    """Check available Ollama models for TTS/STT"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return {
                'status': 'available',
                'models': [model['name'] for model in models],
                'count': len(models)
            }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'models': [],
            'count': 0
        }

def check_audio_dependencies():
    """Check if audio processing dependencies are available"""
    dependencies = {
        'portaudio': False,
        'pyaudio': False,
        'speechrecognition': False,
        'pyttsx3': False,
        'whisper': False
    }
    
    # Check for system audio libraries
    try:
        import subprocess
        result = subprocess.run(['python', '-c', 'import pyaudio'], 
                              capture_output=True, text=True)
        dependencies['pyaudio'] = result.returncode == 0
    except:
        pass
    
    try:
        import subprocess
        result = subprocess.run(['python', '-c', 'import speech_recognition'], 
                              capture_output=True, text=True)
        dependencies['speechrecognition'] = result.returncode == 0
    except:
        pass
        
    try:
        import subprocess
        result = subprocess.run(['python', '-c', 'import pyttsx3'], 
                              capture_output=True, text=True)
        dependencies['pyttsx3'] = result.returncode == 0
    except:
        pass
    
    return dependencies

def check_audio_devices():
    """Check available audio input/output devices"""
    try:
        # Try to detect audio devices using Python
        result = subprocess.run([
            'python', '-c', 
            'import pyaudio; p=pyaudio.PyAudio(); print("Audio devices:", p.get_device_count())'
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            return {
                'status': 'available',
                'details': result.stdout.strip()
            }
    except:
        pass
    
    return {
        'status': 'unavailable',
        'details': 'Could not detect audio devices'
    }

def get_recommended_models():
    """Get list of recommended TTS/STT models"""
    return {
        'speech_to_text': [
            {
                'name': 'whisper:base',
                'size': '142MB',
                'quality': 'good',
                'speed': 'fast',
                'command': 'ollama pull whisper:base',
                'description': 'OpenAI Whisper base model for speech recognition'
            },
            {
                'name': 'whisper:small',
                'size': '465MB', 
                'quality': 'better',
                'speed': 'medium',
                'command': 'ollama pull whisper:small',
                'description': 'OpenAI Whisper small model with better accuracy'
            }
        ],
        'text_to_speech': [
            {
                'name': 'bark',
                'size': '2.8GB',
                'quality': 'excellent',
                'features': 'multilingual, realistic voices',
                'command': 'ollama pull bark',
                'description': 'Bark TTS model with realistic voice synthesis'
            },
            {
                'name': 'tortoise-tts',
                'size': '1.2GB',
                'quality': 'very good',
                'features': 'voice cloning, expressive',
                'command': 'ollama pull tortoise-tts',
                'description': 'Tortoise TTS for expressive voice synthesis'
            }
        ],
        'conversational': [
            {
                'name': 'llama3.2:latest',
                'size': '2GB',
                'purpose': 'Oliver brain',
                'command': 'ollama pull llama3.2:latest',
                'description': 'Main conversational AI model for Oliver'
            }
        ]
    }

def assess_readiness():
    """Assess overall TTS/STT readiness"""
    ollama_status = check_ollama_models()
    audio_deps = check_audio_dependencies()
    audio_devices = check_audio_devices()
    recommended = get_recommended_models()
    
    # Calculate readiness scores
    ollama_ready = ollama_status['status'] == 'available' and ollama_status['count'] > 0
    
    # Check for TTS/STT specific models
    available_models = ollama_status.get('models', [])
    has_whisper = any('whisper' in model.lower() for model in available_models)
    has_tts = any(model.lower() in ['bark', 'tortoise-tts'] for model in available_models)
    has_llm = any('llama' in model.lower() or 'mistral' in model.lower() for model in available_models)
    
    deps_ready = sum(audio_deps.values()) >= 2  # At least 2 audio dependencies
    devices_ready = audio_devices['status'] == 'available'
    
    overall_score = sum([
        ollama_ready * 30,
        has_whisper * 25,
        has_tts * 25,
        deps_ready * 10,
        devices_ready * 10
    ])
    
    readiness_report = {
        'timestamp': datetime.now().isoformat(),
        'overall_readiness': {
            'score': overall_score,
            'grade': 'A' if overall_score >= 90 else 'B' if overall_score >= 75 else 'C' if overall_score >= 60 else 'D',
            'status': 'Ready' if overall_score >= 75 else 'Partially Ready' if overall_score >= 50 else 'Not Ready'
        },
        'components': {
            'ollama_service': {
                'ready': ollama_ready,
                'status': ollama_status['status'],
                'models_count': ollama_status['count'],
                'available_models': available_models[:10]  # Limit output
            },
            'stt_models': {
                'ready': has_whisper,
                'available': [m for m in available_models if 'whisper' in m.lower()],
                'recommended': recommended['speech_to_text']
            },
            'tts_models': {
                'ready': has_tts,
                'available': [m for m in available_models if any(tts in m.lower() for tts in ['bark', 'tortoise'])],
                'recommended': recommended['text_to_speech']
            },
            'llm_models': {
                'ready': has_llm,
                'available': [m for m in available_models if any(llm in m.lower() for llm in ['llama', 'mistral', 'qwen'])],
                'recommended': recommended['conversational']
            },
            'audio_dependencies': {
                'ready': deps_ready,
                'details': audio_deps
            },
            'audio_devices': {
                'ready': devices_ready,
                'details': audio_devices
            }
        },
        'next_steps': [],
        'oliver_integration': {
            'voice_conversation_ready': has_whisper and has_tts and has_llm,
            'text_conversation_ready': has_llm,
            'real_time_processing_ready': overall_score >= 75
        }
    }
    
    # Generate next steps
    if not ollama_ready:
        readiness_report['next_steps'].append('Start Ollama service: docker-compose up -d ollama')
    
    if not has_whisper:
        readiness_report['next_steps'].append('Install Whisper for STT: ollama pull whisper:base')
    
    if not has_tts:
        readiness_report['next_steps'].append('Install TTS model: ollama pull bark')
    
    if not has_llm:
        readiness_report['next_steps'].append('Install LLM for Oliver: ollama pull llama3.2:latest')
    
    if not deps_ready:
        readiness_report['next_steps'].append('Install audio dependencies: pip install pyaudio speechrecognition pyttsx3')
    
    return readiness_report

def main():
    """Main function"""
    try:
        report = assess_readiness()
        print(json.dumps(report, indent=2))
        return 0
    except Exception as e:
        error_report = {
            'error': True,
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }
        print(json.dumps(error_report, indent=2))
        return 1

if __name__ == '__main__':
    sys.exit(main())
