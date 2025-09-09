@echo off
cd /d "C:\AI Projects\self-hosted-ai-starter-kit"

echo Loading environment variables from .env file...

REM Read and set environment variables from .env file
for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
    if not "%%a"=="" if not "%%a:~0,1%"=="#" (
        set "%%a=%%b"
        echo Set %%a
    )
)

echo Starting Fast Whisper API with loaded environment...
"C:\AI Projects\self-hosted-ai-starter-kit\.venv\Scripts\python.exe" scripts\fast_whisper_api.py

pause
