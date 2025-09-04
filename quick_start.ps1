# HR Assistant Chatbot API - Quick Start & Test Script
# This script helps start the server and run tests

param(
    [switch]$StartServer,
    [switch]$RunTests,
    [switch]$Both,
    [string]$Port = "8000"
)

$ErrorActionPreference = "Stop"

function Write-ColoredOutput {
    param([string]$Message, [string]$Color = "White")
    
    switch ($Color) {
        "Red" { Write-Host $Message -ForegroundColor Red }
        "Green" { Write-Host $Message -ForegroundColor Green }
        "Yellow" { Write-Host $Message -ForegroundColor Yellow }
        "Blue" { Write-Host $Message -ForegroundColor Blue }
        "Cyan" { Write-Host $Message -ForegroundColor Cyan }
        "Purple" { Write-Host $Message -ForegroundColor Magenta }
        default { Write-Host $Message }
    }
}

function Show-Usage {
    Write-ColoredOutput "HR Assistant Chatbot API - Quick Start & Test" "Yellow"
    Write-ColoredOutput "=" * 50 "Yellow"
    Write-Host ""
    Write-ColoredOutput "Usage:" "Cyan"
    Write-Host "  .\quick_start.ps1 -StartServer    # Start the FastAPI server"
    Write-Host "  .\quick_start.ps1 -RunTests      # Run all test suites"
    Write-Host "  .\quick_start.ps1 -Both          # Start server and run tests"
    Write-Host "  .\quick_start.ps1 -Port 8080     # Use custom port"
    Write-Host ""
    Write-ColoredOutput "Examples:" "Cyan"
    Write-Host "  .\quick_start.ps1 -Both"
    Write-Host "  .\quick_start.ps1 -StartServer -Port 8080"
    Write-Host ""
}

function Test-PythonInstallation {
    Write-ColoredOutput "🔍 Checking Python installation..." "Blue"
    
    try {
        $pythonVersion = python --version 2>&1
        Write-ColoredOutput "✅ Python found: $pythonVersion" "Green"
        return $true
    } catch {
        Write-ColoredOutput "❌ Python not found. Please install Python 3.7+" "Red"
        return $false
    }
}

function Test-Dependencies {
    Write-ColoredOutput "📦 Checking dependencies..." "Blue"
    
    $requiredPackages = @("fastapi", "uvicorn", "sqlalchemy", "requests")
    $missingPackages = @()
    
    foreach ($package in $requiredPackages) {
        try {
            $result = python -c "import $package" 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-ColoredOutput "✅ $package is installed" "Green"
            } else {
                $missingPackages += $package
            }
        } catch {
            $missingPackages += $package
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-ColoredOutput "❌ Missing packages: $($missingPackages -join ', ')" "Red"
        Write-ColoredOutput "Installing missing packages..." "Yellow"
        
        try {
            pip install $missingPackages
            Write-ColoredOutput "✅ Dependencies installed successfully" "Green"
        } catch {
            Write-ColoredOutput "❌ Failed to install dependencies" "Red"
            return $false
        }
    }
    
    return $true
}

function Start-ApiServer {
    param([string]$Port)
    
    Write-ColoredOutput "🚀 Starting FastAPI server on port $Port..." "Blue"
    
    # Check if port is available
    try {
        $connection = Test-NetConnection -ComputerName "localhost" -Port $Port -WarningAction SilentlyContinue
        if ($connection.TcpTestSucceeded) {
            Write-ColoredOutput "⚠️  Port $Port is already in use" "Yellow"
            $response = Read-Host "Continue anyway? (y/n)"
            if ($response -ne "y") {
                return $false
            }
        }
    } catch {
        # Test-NetConnection might not be available on all systems
    }
    
    # Start the server
    try {
        Write-ColoredOutput "Starting server..." "Green"
        Write-ColoredOutput "Server will be available at: http://localhost:$Port" "Cyan"
        Write-ColoredOutput "Press Ctrl+C to stop the server" "Yellow"
        Write-Host ""
        
        # Start uvicorn server
        python -m uvicorn app.main:app --host 0.0.0.0 --port $Port --reload
        
    } catch {
        Write-ColoredOutput "❌ Failed to start server: $($_.Exception.Message)" "Red"
        return $false
    }
    
    return $true
}

function Wait-ForServer {
    param([string]$Port)
    
    Write-ColoredOutput "⏳ Waiting for server to be ready..." "Blue"
    
    $maxAttempts = 30
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:$Port/health" -TimeoutSec 2 -ErrorAction Stop
            Write-ColoredOutput "✅ Server is ready!" "Green"
            return $true
        } catch {
            $attempt++
            Start-Sleep -Seconds 1
            Write-Host "." -NoNewline
        }
    }
    
    Write-Host ""
    Write-ColoredOutput "❌ Server failed to start within 30 seconds" "Red"
    return $false
}

function Run-TestSuites {
    Write-ColoredOutput "🧪 Running test suites..." "Blue"
    
    # Run Python test runner
    if (Test-Path "run_all_tests.py") {
        Write-ColoredOutput "Running comprehensive Python tests..." "Cyan"
        try {
            python run_all_tests.py
            $pythonTestsExitCode = $LASTEXITCODE
        } catch {
            Write-ColoredOutput "❌ Python tests failed to run" "Red"
            $pythonTestsExitCode = 1
        }
    } else {
        Write-ColoredOutput "⚠️  run_all_tests.py not found, skipping Python tests" "Yellow"
        $pythonTestsExitCode = 0
    }
    
    # Run PowerShell simple tests
    if (Test-Path "test_simple.ps1") {
        Write-ColoredOutput "`nRunning PowerShell simple tests..." "Cyan"
        try {
            .\test_simple.ps1
            $powershellTestsExitCode = $LASTEXITCODE
        } catch {
            Write-ColoredOutput "❌ PowerShell tests failed to run" "Red"
            $powershellTestsExitCode = 1
        }
    } else {
        Write-ColoredOutput "⚠️  test_simple.ps1 not found, skipping PowerShell tests" "Yellow"
        $powershellTestsExitCode = 0
    }
    
    # Summary
    Write-ColoredOutput "`n📊 Test Summary:" "Yellow"
    if ($pythonTestsExitCode -eq 0 -and $powershellTestsExitCode -eq 0) {
        Write-ColoredOutput "✅ All test suites passed!" "Green"
        return $true
    } else {
        Write-ColoredOutput "❌ Some test suites failed" "Red"
        return $false
    }
}

function Start-ServerAndRunTests {
    param([string]$Port)
    
    Write-ColoredOutput "🚀 Starting server and running tests..." "Blue"
    
    # Start server in background
    $serverJob = Start-Job -ScriptBlock {
        param($Port)
        Set-Location $using:PWD
        python -m uvicorn app.main:app --host 0.0.0.0 --port $Port --reload
    } -ArgumentList $Port
    
    try {
        # Wait for server to be ready
        if (Wait-ForServer -Port $Port) {
            # Run tests
            $testResult = Run-TestSuites
            
            Write-ColoredOutput "`n🏁 Test execution completed!" "Yellow"
            return $testResult
        } else {
            Write-ColoredOutput "❌ Could not start server for testing" "Red"
            return $false
        }
    } finally {
        # Stop the server
        Write-ColoredOutput "`n🛑 Stopping server..." "Yellow"
        Stop-Job -Job $serverJob -Force
        Remove-Job -Job $serverJob -Force
    }
}

# Main execution
Write-ColoredOutput "🤖 HR Assistant Chatbot API - Quick Start" "Yellow"
Write-ColoredOutput "=" * 50 "Yellow"

# Show usage if no parameters
if (-not $StartServer -and -not $RunTests -and -not $Both) {
    Show-Usage
    exit 0
}

# Check prerequisites
if (-not (Test-PythonInstallation)) {
    exit 1
}

if (-not (Test-Dependencies)) {
    exit 1
}

# Change to script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

try {
    if ($Both) {
        $success = Start-ServerAndRunTests -Port $Port
        if ($success) {
            Write-ColoredOutput "`n🎉 All operations completed successfully!" "Green"
            exit 0
        } else {
            Write-ColoredOutput "`n💥 Some operations failed" "Red"
            exit 1
        }
    } elseif ($StartServer) {
        Start-ApiServer -Port $Port
    } elseif ($RunTests) {
        # Check if server is running
        try {
            Invoke-RestMethod -Uri "http://localhost:$Port/health" -TimeoutSec 2 | Out-Null
            $success = Run-TestSuites
            if ($success) {
                exit 0
            } else {
                exit 1
            }
        } catch {
            Write-ColoredOutput "❌ Server not running on port $Port. Please start the server first." "Red"
            Write-ColoredOutput "Use: .\quick_start.ps1 -StartServer" "Yellow"
            exit 1
        }
    }
} catch {
    Write-ColoredOutput "💥 Unexpected error: $($_.Exception.Message)" "Red"
    exit 1
}
