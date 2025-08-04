# PowerShell Commands for Environment Verification

## Option 1: Direct Virtual Environment Activation + Verify Setup
```powershell
# Check if virtual environment exists and activate it, then run verify_setup.py
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "🔧 Activating virtual environment..." -ForegroundColor Green
    & ".\.venv\Scripts\Activate.ps1"
    Write-Host "🚀 Running verify_setup.py..." -ForegroundColor Green
    python verify_setup.py
} elseif (Test-Path ".\ai-starter-kit\Scripts\Activate.ps1") {
    Write-Host "🔧 Activating conda environment..." -ForegroundColor Green
    & ".\ai-starter-kit\Scripts\Activate.ps1"
    Write-Host "🚀 Running verify_setup.py..." -ForegroundColor Green
    python verify_setup.py
} else {
    Write-Host "⚠️  No virtual environment found, using system Python..." -ForegroundColor Yellow
    python verify_setup.py
}
```

## Option 2: Using the Environment Checker Script
```powershell
# Run our custom environment checker that handles everything
python run_verify.py
```

## Option 3: Direct Python Executable (Most Reliable)
```powershell
# Use the specific Python executable from virtual environment
& "C:/AI Projects/self-hosted-ai-starter-kit/.venv/Scripts/python.exe" verify_setup.py
```

## Option 4: Conda Environment Check + Activation
```powershell
# Check conda environment status and activate if needed
$condaEnv = conda env list | Select-String "ai-starter-kit"
if ($condaEnv) {
    Write-Host "🔧 Activating conda environment: ai-starter-kit" -ForegroundColor Green
    conda activate ai-starter-kit
    python verify_setup.py
} else {
    Write-Host "⚠️  Conda environment 'ai-starter-kit' not found" -ForegroundColor Yellow
    Write-Host "💡 Using virtual environment instead..." -ForegroundColor Blue
    & ".\.venv\Scripts\python.exe" verify_setup.py
}
```

## Option 5: Complete Environment Check and Setup
```powershell
# Comprehensive environment verification and setup
function Check-And-Run-Verify {
    Write-Host "🔍 Checking Python environment..." -ForegroundColor Cyan
    
    # Check for virtual environment
    if (Test-Path ".\.venv\Scripts\python.exe") {
        Write-Host "✅ Virtual environment found" -ForegroundColor Green
        $pythonExe = ".\.venv\Scripts\python.exe"
    }
    # Check for conda environment
    elseif (Test-Path ".\ai-starter-kit\Scripts\python.exe") {
        Write-Host "✅ Conda environment found" -ForegroundColor Green
        $pythonExe = ".\ai-starter-kit\Scripts\python.exe"
    }
    # Fallback to system Python
    else {
        Write-Host "⚠️  Using system Python" -ForegroundColor Yellow
        $pythonExe = "python"
    }
    
    Write-Host "🚀 Running verify_setup.py with: $pythonExe" -ForegroundColor Green
    Write-Host "=" * 60
    
    & $pythonExe verify_setup.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Verification completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Verification completed with warnings" -ForegroundColor Yellow
    }
}

# Run the function
Check-And-Run-Verify
```

## Recommended Commands for Different Scenarios:

### For Daily Use (Simple):
```powershell
python run_verify.py
```

### For Development (Explicit):
```powershell
& ".\.venv\Scripts\python.exe" verify_setup.py
```

### For CI/CD or Automation:
```powershell
if (Test-Path ".\.venv\Scripts\python.exe") {
    & ".\.venv\Scripts\python.exe" verify_setup.py
} else {
    Write-Error "Virtual environment not found"
    exit 1
}
```

### For Troubleshooting:
```powershell
# Show current Python info
Write-Host "Current Python:" (Get-Command python).Source
Write-Host "Python Version:" (python --version)
Write-Host "Virtual Env Check:" (Test-Path ".\.venv\Scripts\python.exe")

# Then run verification
& ".\.venv\Scripts\python.exe" verify_setup.py
```
