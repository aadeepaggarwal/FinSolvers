@echo off
echo RAG Policy QA System - Setup Script
echo ====================================

echo.
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Running system tests...
python test_rag_system.py

echo.
echo Setup complete!
echo.
echo To use the system:
echo 1. Set your OpenAI API key (optional but recommended):
echo    $env:OPENAI_API_KEY = "your-openai-api-key"
echo.
echo 2. Run a query:
echo    python rag_policy_qa.py --policy "./Sample data/EDLHLGA23009V012223.pdf" --query "your query here"
echo.
echo 3. Or start the API server:
echo    python rag_policy_qa.py --api
echo.
pause
