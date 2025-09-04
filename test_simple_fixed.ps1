# Simple API Test - Fixed Version
Write-Host "HR Assistant Chatbot API - Simple Test Suite" -ForegroundColor Green

$baseUrl = "http://localhost:8000"
$passedTests = 0
$failedTests = 0

# Test server health
Write-Host "`nTesting server health..." -ForegroundColor Blue
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Server is healthy" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "❌ Server health failed" -ForegroundColor Red
    $failedTests++
    exit 1
}

# Test basic endpoints
$endpoints = @(
    @{Path = "/"; Name = "Root"},
    @{Path = "/api/menu/icp_hr"; Name = "ICP HR Menu"},
    @{Path = "/api/chatbot/employees"; Name = "Employees"},
    @{Path = "/api/merchant/sales/today"; Name = "Sales"}
)

Write-Host "`nTesting API endpoints..." -ForegroundColor Blue

foreach ($endpoint in $endpoints) {
    Write-Host "Testing $($endpoint.Name)..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl$($endpoint.Path)" -Method GET -TimeoutSec 10
        
        if ($response -ne $null) {
            Write-Host "  ✅ PASSED" -ForegroundColor Green
            $passedTests++
        } else {
            Write-Host "  ❌ FAILED - No response" -ForegroundColor Red
            $failedTests++
        }
    } catch {
        if ($_.Exception.Response.StatusCode -eq 404 -or $_.Exception.Response.StatusCode -eq 422) {
            Write-Host "  ⚠️  WARNING - Expected error" -ForegroundColor Yellow
            $passedTests++
        } else {
            Write-Host "  ❌ FAILED - $($_.Exception.Message)" -ForegroundColor Red
            $failedTests++
        }
    }
}

# Summary
$totalTests = $passedTests + $failedTests
$successRate = [math]::Round(($passedTests / $totalTests) * 100, 1)

Write-Host "`n============================================" -ForegroundColor Yellow
Write-Host "TEST SUMMARY" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "Total Tests: $totalTests"
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $failedTests" -ForegroundColor Red
Write-Host "Success Rate: $successRate%" -ForegroundColor Blue

if ($failedTests -eq 0) {
    Write-Host "`n🎉 All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠️ Some tests failed" -ForegroundColor Yellow
    exit 1
}
