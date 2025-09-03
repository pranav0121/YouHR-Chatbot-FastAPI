# Retention Executor API Test Script
# Tests all 18 endpoints of the Retention Executor system

Write-Host "🔧 Starting Retention Executor API Tests..." -ForegroundColor Green
Write-Host "=" * 60

$baseUrl = "http://localhost:8000/api/icp/executor"
$testResults = @()

# Define all endpoints to test
$endpoints = @(
    @{ Name = "Assigned Merchants"; Url = "$baseUrl/assigned-merchants"; Category = "Daily Activity" },
    @{ Name = "Daily Schedule"; Url = "$baseUrl/daily-schedule"; Category = "Daily Activity" },
    @{ Name = "Task Completion"; Url = "$baseUrl/task-completion"; Category = "Daily Activity" },
    @{ Name = "Merchant Profile"; Url = "$baseUrl/merchant-profile?merchant_id=M001"; Category = "Merchant Follow-up" },
    @{ Name = "Follow-up Schedule"; Url = "$baseUrl/follow-up-schedule"; Category = "Merchant Follow-up" },
    @{ Name = "Retention Metrics"; Url = "$baseUrl/retention-metrics"; Category = "Merchant Follow-up" },
    @{ Name = "New Merchants"; Url = "$baseUrl/new-merchants"; Category = "Onboarding Support" },
    @{ Name = "Onboarding Progress"; Url = "$baseUrl/onboarding-progress"; Category = "Onboarding Support" },
    @{ Name = "Training Schedule"; Url = "$baseUrl/training-schedule"; Category = "Onboarding Support" },
    @{ Name = "Priority Alerts"; Url = "$baseUrl/priority-alerts"; Category = "Notifications" },
    @{ Name = "System Notifications"; Url = "$baseUrl/system-notifications"; Category = "Notifications" },
    @{ Name = "Communication Log"; Url = "$baseUrl/communication-log"; Category = "Notifications" },
    @{ Name = "Pending Tickets"; Url = "$baseUrl/pending-tickets"; Category = "Support Requests" },
    @{ Name = "Escalation Queue"; Url = "$baseUrl/escalation-queue"; Category = "Support Requests" },
    @{ Name = "Resolution Tracking"; Url = "$baseUrl/resolution-tracking"; Category = "Support Requests" },
    @{ Name = "Merchant Feedback"; Url = "$baseUrl/merchant-feedback"; Category = "Feedback" },
    @{ Name = "Satisfaction Survey"; Url = "$baseUrl/satisfaction-survey"; Category = "Feedback" },
    @{ Name = "Improvement Suggestions"; Url = "$baseUrl/improvement-suggestions"; Category = "Feedback" }
)

# Test each endpoint
$totalTests = $endpoints.Count
$passedTests = 0
$failedTests = 0

foreach ($endpoint in $endpoints) {
    Write-Host "Testing: $($endpoint.Name) [$($endpoint.Category)]" -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri $endpoint.Url -Method GET -TimeoutSec 10
        
        if ($response.status -eq "success") {
            Write-Host "  ✅ PASSED - Status: $($response.status)" -ForegroundColor Green
            $passedTests++
            $testResults += @{
                Endpoint  = $endpoint.Name
                Category  = $endpoint.Category
                Status    = "PASSED"
                Response  = "Success"
                Timestamp = $response.timestamp
            }
        }
        else {
            Write-Host "  ❌ FAILED - Unexpected status: $($response.status)" -ForegroundColor Red
            $failedTests++
            $testResults += @{
                Endpoint  = $endpoint.Name
                Category  = $endpoint.Category
                Status    = "FAILED"
                Response  = "Unexpected status"
                Timestamp = "N/A"
            }
        }
    }
    catch {
        Write-Host "  ❌ FAILED - Error: $($_.Exception.Message)" -ForegroundColor Red
        $failedTests++
        $testResults += @{
            Endpoint  = $endpoint.Name
            Category  = $endpoint.Category
            Status    = "FAILED"
            Response  = $_.Exception.Message
            Timestamp = "N/A"
        }
    }
    
    Start-Sleep -Milliseconds 200  # Small delay between requests
}

# Summary Report
Write-Host ""
Write-Host "=" * 60
Write-Host "📊 TEST SUMMARY REPORT" -ForegroundColor Cyan
Write-Host "=" * 60

Write-Host "Total Tests: $totalTests" -ForegroundColor White
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $failedTests" -ForegroundColor Red
Write-Host "Success Rate: $([math]::Round(($passedTests / $totalTests) * 100, 2))%" -ForegroundColor $(if ($passedTests -eq $totalTests) { "Green" } else { "Yellow" })

# Detailed Results by Category
Write-Host ""
Write-Host "📋 RESULTS BY CATEGORY:" -ForegroundColor Cyan

$categories = $testResults | Group-Object Category
foreach ($category in $categories) {
    Write-Host ""
    Write-Host "  $($category.Name):" -ForegroundColor White
    foreach ($test in $category.Group) {
        $statusColor = if ($test.Status -eq "PASSED") { "Green" } else { "Red" }
        Write-Host "    • $($test.Endpoint): $($test.Status)" -ForegroundColor $statusColor
    }
}

# Failed Tests Details
if ($failedTests -gt 0) {
    Write-Host ""
    Write-Host "❌ FAILED TESTS DETAILS:" -ForegroundColor Red
    $failedTestDetails = $testResults | Where-Object { $_.Status -eq "FAILED" }
    foreach ($failed in $failedTestDetails) {
        Write-Host "  • $($failed.Endpoint): $($failed.Response)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎉 Retention Executor API Testing Complete!" -ForegroundColor Green
Write-Host "=" * 60

# Save results to JSON file
$resultsJson = $testResults | ConvertTo-Json -Depth 3
$resultsJson | Out-File -FilePath "retention_executor_test_results.json" -Encoding UTF8
Write-Host "📄 Test results saved to: retention_executor_test_results.json" -ForegroundColor Cyan
