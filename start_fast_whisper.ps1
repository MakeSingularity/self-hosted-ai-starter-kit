# Load environment variables from .env file and start Fast Whisper API

Write-Host "🚀 Starting Fast Whisper API with .env support" -ForegroundColor Green

# Change to project directory
Set-Location "C:\AI Projects\self-hosted-ai-starter-kit"

# Load .env file
if (Test-Path ".env") {
    Write-Host "📁 Loading environment from .env file..." -ForegroundColor Yellow
    
    Get-Content ".env" | ForEach-Object {
        if ($_ -and !$_.StartsWith("#") -and $_.Contains("=")) {
            $key, $value = $_.Split("=", 2)
            Set-Item -Path "env:$key" -Value $value
            
            if ($key -like "*TOKEN*") {
                Write-Host "✅ Loaded $key (hidden)" -ForegroundColor Green
            }
            else {
                Write-Host "✅ Loaded $key=$value" -ForegroundColor Green
            }
        }
    }
    
    # Check bot token
    if ($env:TELEGRAM_BOT_TOKEN) {
        $tokenPreview = $env:TELEGRAM_BOT_TOKEN.Substring(0, [Math]::Min(10, $env:TELEGRAM_BOT_TOKEN.Length))
        Write-Host "✅ Telegram bot token loaded: $tokenPreview..." -ForegroundColor Green
    }
    else {
        Write-Host "❌ Telegram bot token not found" -ForegroundColor Red
    }
}
else {
    Write-Host "⚠️ No .env file found" -ForegroundColor Yellow
}

Write-Host "🎤 Starting Fast Whisper API server..." -ForegroundColor Cyan
Write-Host "📡 Access at: http://localhost:8000" -ForegroundColor Blue
Write-Host "📚 API docs at: http://localhost:8000/docs" -ForegroundColor Blue

# Start the API
& "C:\AI Projects\self-hosted-ai-starter-kit\.venv\Scripts\python.exe" scripts\fast_whisper_api.py
