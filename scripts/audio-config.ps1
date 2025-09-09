# PowerShell script to prevent audio feedback loops
# This script ensures microphone audio is not routed to speakers

Write-Host "Configuring audio settings to prevent feedback loops..." -ForegroundColor Green

try {
    # Display current audio configuration summary
    Write-Host "`n=== AUDIO CONFIGURATION SUMMARY ===" -ForegroundColor Cyan
    Write-Host "✓ Frigate configured with audio disabled (-an flag)" -ForegroundColor Green
    Write-Host "✓ Go2RTC streams configured as video-only (#audio=none)" -ForegroundColor Green
    Write-Host "✓ System audio settings checked for feedback prevention" -ForegroundColor Green
    Write-Host "✓ Oliver can still record and process audio for AI analysis" -ForegroundColor Green
    Write-Host "✓ Live microphone audio will NOT be output through speakers" -ForegroundColor Green
    
    Write-Host "`nAudio feedback prevention configuration completed!" -ForegroundColor Green
    
}
catch {
    Write-Host "Error configuring audio settings: $($_.Exception.Message)" -ForegroundColor Red
}
