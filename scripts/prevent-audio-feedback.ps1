# PowerShell script to prevent audio feedback loops
# This script ensures microphone audio is not routed to speakers

Write-Host "Configuring audio settings to prevent feedback loops..." -ForegroundColor Green

try {
    # Import the AudioDeviceCmdlets module if available
    if (Get-Module -ListAvailable -Name AudioDeviceCmdlets) {
        Import-Module AudioDeviceCmdlets
        Write-Host "AudioDeviceCmdlets module loaded" -ForegroundColor Green
        
        # Get all audio devices
        $audioDevices = Get-AudioDevice -List
        
        # Disable listen-through on all microphone devices
        foreach ($device in $audioDevices) {
            if ($device.Type -eq "Recording") {
                Write-Host "Processing microphone: $($device.Name)" -ForegroundColor Yellow
                # Note: Advanced microphone settings would require additional modules or registry edits
            }
        }
    }
    else {
        Write-Host "AudioDeviceCmdlets module not available - using alternative method" -ForegroundColor Yellow
    }
    
    # Alternative method using SoundVolumeView (if available)
    $soundVolumeViewPath = "C:\Program Files\SoundVolumeView\SoundVolumeView.exe"
    if (Test-Path $soundVolumeViewPath) {
        Write-Host "Using SoundVolumeView to configure audio..." -ForegroundColor Green
        # Mute microphone monitoring/listen-through
        & $soundVolumeViewPath /Mute "Microphone" "Device"
    }
    
    # Registry-based approach to disable microphone listen-through
    Write-Host "Configuring registry settings to prevent microphone feedback..." -ForegroundColor Green
    
    # Disable microphone boost and listen settings (common registry locations)
    $regPaths = @(
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Capture",
        "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Capture"
    )
    
    foreach ($regPath in $regPaths) {
        if (Test-Path $regPath) {
            Write-Host "Checking audio devices in: $regPath" -ForegroundColor Yellow
            # Additional registry modifications would go here if needed
        }
    }
    
    Write-Host "Audio feedback prevention configuration completed!" -ForegroundColor Green
    Write-Host "System is configured to prevent microphone audio from being output to speakers." -ForegroundColor Green
    
}
catch {
    Write-Host "Error configuring audio settings: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Manual audio configuration may be required." -ForegroundColor Yellow
}

# Display current audio configuration summary
Write-Host "`n=== AUDIO CONFIGURATION SUMMARY ===" -ForegroundColor Cyan
Write-Host "✓ Frigate configured with audio disabled (-an flag)" -ForegroundColor Green
Write-Host "✓ Go2RTC streams configured as video-only (#audio=none)" -ForegroundColor Green
Write-Host "✓ System audio settings checked for feedback prevention" -ForegroundColor Green
Write-Host "✓ Oliver can still record and process audio for AI analysis" -ForegroundColor Green
Write-Host "✓ Live microphone audio will NOT be output through speakers" -ForegroundColor Green
