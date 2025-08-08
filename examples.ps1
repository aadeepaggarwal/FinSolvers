# RAG Policy QA System - Example Usage Script
# This PowerShell script demonstrates various ways to use the system

Write-Host "RAG Policy QA System - Example Usage" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Check if Python is available
Write-Host "`nChecking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Set OpenAI API key (optional)
Write-Host "`nSetting up OpenAI API key..." -ForegroundColor Yellow
$apiKey = $env:OPENAI_API_KEY
if (-not $apiKey) {
    Write-Host "⚠ No OpenAI API key found in environment variables" -ForegroundColor Yellow
    Write-Host "  The system will use fallback reasoning instead of GPT-4" -ForegroundColor Yellow
    Write-Host "  To enable LLM features, set: `$env:OPENAI_API_KEY = 'your-key-here'" -ForegroundColor Yellow
} else {
    Write-Host "✓ OpenAI API key found" -ForegroundColor Green
}

# Example queries
Write-Host "`nExample Queries:" -ForegroundColor Green
Write-Host "=================" -ForegroundColor Green

$sampleQueries = @(
    @{
        Description = "Medical procedure coverage query"
        Query = "46-year-old male, knee surgery in Pune, 3-month-old policy"
        PDF = "EDLHLGA23009V012223.pdf"
    },
    @{
        Description = "Pre-existing condition coverage"
        Query = "What are the exclusions for pre-existing conditions?"
        PDF = "BAJHLIP23020V012223.pdf"
    },
    @{
        Description = "Emergency hospitalization limits"
        Query = "Emergency hospitalization coverage limits"
        PDF = "CHOTGDP23004V012223.pdf"
    },
    @{
        Description = "Maternity benefits waiting period"
        Query = "Maternity benefits waiting period"
        PDF = "EDLHLGA23009V012223.pdf"
    }
)

foreach ($example in $sampleQueries) {
    Write-Host "`n$($example.Description):" -ForegroundColor Cyan
    $pdfPath = "./Sample data/$($example.PDF)"
    
    # Check if PDF exists
    if (Test-Path $pdfPath) {
        Write-Host "Command: python rag_policy_qa.py --policy `"$pdfPath`" --query `"$($example.Query)`"" -ForegroundColor Gray
        
        # Ask user if they want to run this example
        $response = Read-Host "Run this example? (y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            Write-Host "Running query..." -ForegroundColor Yellow
            python rag_policy_qa.py --policy $pdfPath --query $example.Query
            Write-Host "`nQuery completed.`n" -ForegroundColor Green
        }
    } else {
        Write-Host "PDF file not found: $pdfPath" -ForegroundColor Red
    }
}

# API Mode Example
Write-Host "`nAPI Mode Example:" -ForegroundColor Green
Write-Host "=================" -ForegroundColor Green
Write-Host "To start the API server:" -ForegroundColor Cyan
Write-Host "python rag_policy_qa.py --api --port 5000" -ForegroundColor Gray
Write-Host "`nThen test with curl:" -ForegroundColor Cyan
Write-Host @"
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "policy_path": "./Sample data/EDLHLGA23009V012223.pdf",
    "query": "46M, knee surgery, Pune, 3-month policy"
  }'
"@ -ForegroundColor Gray

$response = Read-Host "`nStart API server? (y/N)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "Starting API server on port 5000..." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    python rag_policy_qa.py --api --port 5000
}

Write-Host "`nFor more information, see README.md" -ForegroundColor Green
