"""
FastAPI server that provides AI services to n8n workflows
Run this server and use HTTP Request nodes in n8n to call the endpoints

Usage:
1. Activate your conda environment: conda activate ai-starter-kit
2. Run the server: python examples/api_server.py
3. Use HTTP Request nodes in n8n to call: http://localhost:8000/process-text
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="n8n AI Integration API",
    description="Local AI services for n8n workflows",
    version="1.0.0"
)

class TextProcessRequest(BaseModel):
    text: str
    operation: str = "summarize"  # summarize, sentiment, extract_entities
    options: Optional[dict] = None

class TextProcessResponse(BaseModel):
    result: dict
    status: str
    operation: str

@app.get("/")
async def root():
    return {
        "message": "n8n AI Integration API",
        "endpoints": [
            "/process-text - POST - Process text with AI",
            "/health - GET - Health check",
            "/docs - GET - API documentation"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "n8n-ai-integration"}

@app.post("/process-text", response_model=TextProcessResponse)
async def process_text(request: TextProcessRequest):
    """
    Process text using various AI operations
    """
    try:
        if request.operation == "summarize":
            # Simple summarization (in production, use transformers, etc.)
            words = request.text.split()
            summary = " ".join(words[:min(30, len(words))])
            if len(words) > 30:
                summary += "..."
            
            result = {
                "summary": summary,
                "original_length": len(request.text),
                "word_count": len(words),
                "compression_ratio": len(summary) / len(request.text)
            }
            
        elif request.operation == "sentiment":
            # Sentiment analysis (in production, use proper models)
            text_lower = request.text.lower()
            positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "awesome"]
            negative_words = ["bad", "terrible", "awful", "horrible", "disappointing", "sad", "angry"]
            
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count > neg_count:
                sentiment = "positive"
                confidence = min(0.9, 0.5 + (pos_count - neg_count) * 0.1)
            elif neg_count > pos_count:
                sentiment = "negative" 
                confidence = min(0.9, 0.5 + (neg_count - pos_count) * 0.1)
            else:
                sentiment = "neutral"
                confidence = 0.5
            
            result = {
                "sentiment": sentiment,
                "confidence": confidence,
                "positive_indicators": pos_count,
                "negative_indicators": neg_count
            }
            
        elif request.operation == "extract_entities":
            # Simple entity extraction (in production, use spaCy, etc.)
            import re
            
            # Extract emails
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', request.text)
            
            # Extract phone numbers (simple pattern)
            phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', request.text)
            
            # Extract URLs
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', request.text)
            
            result = {
                "entities": {
                    "emails": emails,
                    "phone_numbers": phones,
                    "urls": urls
                },
                "counts": {
                    "emails": len(emails),
                    "phone_numbers": len(phones),
                    "urls": len(urls)
                }
            }
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation: {request.operation}")
        
        return TextProcessResponse(
            result=result,
            status="success",
            operation=request.operation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/riva-speech")
async def riva_speech_to_text(audio_data: bytes):
    """
    Example endpoint for NVIDIA Riva speech-to-text
    In production, this would connect to your Riva service
    """
    # This is a placeholder - integrate with actual Riva client
    return {
        "transcription": "This would be the transcribed text from Riva",
        "confidence": 0.95,
        "status": "success"
    }

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("API_PORT", 8000))
    
    print(f"🚀 Starting n8n AI Integration API on port {port}")
    print(f"📝 API Documentation: http://localhost:{port}/docs")
    print(f"🔍 Health Check: http://localhost:{port}/health")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
