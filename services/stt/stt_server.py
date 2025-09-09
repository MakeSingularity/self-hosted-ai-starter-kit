import os
import tempfile
import time

import torch
from fastapi import FastAPI, UploadFile, File, HTTPException

# whisper can be the "openai-whisper" package
try:
    import whisper
except Exception:
    whisper = None

app = FastAPI(title="Oliver STT Service")

MODEL_NAME = os.getenv("STT_MODEL", "small")

# choose device
_device = "cuda" if torch.cuda.is_available() else "cpu"

_model = None


def _load_model():
    global _model
    if _model is not None:
        return _model
    if whisper is None:
        raise RuntimeError("whisper package not available - install openai-whisper or faster-whisper")
    # load model onto selected device
    _model = whisper.load_model(MODEL_NAME, device=_device)
    return _model


@app.get("/health")
def health():
    return {"status": "ok", "device": _device, "model": MODEL_NAME}


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...), language: str | None = None):
    """Accepts an uploaded audio file and returns a transcription using Whisper.

    Supported container formats are those ffmpeg understands (wav, mp3, m4a, flac, mp4, etc).
    """
    model = _load_model()

    # Save upload to a temp file
    suffix = os.path.splitext(file.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        options = {}
        if language:
            options["language"] = language
            options["task"] = "transcribe"

        start = time.time()
        result = model.transcribe(tmp_path, **options)
        duration = time.time() - start

        return {
            "text": result.get("text", ""),
            "language": result.get("language", None),
            "segments": result.get("segments", []),
            "duration_s": duration,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
