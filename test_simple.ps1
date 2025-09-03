# Retention Executor API Test Script
Write-Host "Starting Retention Executor API Tests..." -ForegroundColor Green

$baseUrl = "http://localhost:8000/api/icp/executor"
$testResults = @()

# Define all endpoints to test
$endpoints = @(
    "assigned-merchants",
    "daily-schedule", 
    "task-completion",
    "merchant-profile?merchant_id=M001",
    "follow-up-schedule",
    "retention-metrics",
    "new-merchants",
    "onboarding-progress",
    "training-schedule",
    "priority-alerts",
    "system-notifications",
    "communication-log",
    "pending-tickets",
    "escalation-queue",
    "resolution-tracking",
    "merchant-feedback",
    "satisfaction-survey",
    "improvement-suggestions"
)

$passedTests = 0
$failedTests = 0

foreach ($endpoint in $endpoints) {
    Write-Host "Testing: $endpoint" -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/$endpoint" -Method GET -TimeoutSec 10
        
        if ($response.status -eq "success") {
            Write-Host "  PASSED" -ForegroundColor Green
            $passedTests++
        } else {
            Write-Host "  FAILED" -ForegroundColor Red
            $failedTests++
        }
    }
    catch {
        Write-Host "  FAILED - $($_.Exception.Message)" -ForegroundColor Red
        $failedTests++
    }
}

Write-Host ""
Write-Host "TEST SUMMARY:" -ForegroundColor Cyan
Write-Host "Total Tests: $($endpoints.Count)"
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $failedTests" -ForegroundColor Red
Write-Host "Success Rate: $([math]::Round(($passedTests / $endpoints.Count) * 100, 2))%"
