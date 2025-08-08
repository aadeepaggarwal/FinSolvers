@echo off
echo =====================================================
echo       RAG Policy QA System - Quick Launcher
echo =====================================================
echo.
echo Choose your interface:
echo.
echo 1. Streamlit App (Modern UI)
echo 2. Flask Web App (Professional UI)  
echo 3. Command Line Interface
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting Streamlit application...
    echo Open your browser to: http://localhost:8501
    echo.
    C:\Users\aadee\OneDrive\Desktop\Bajaj\.venv\Scripts\python.exe -m streamlit run streamlit_app.py --server.port 8501
) else if "%choice%"=="2" (
    echo.
    echo Starting Flask web application...
    echo Open your browser to: http://localhost:5001
    echo.
    C:\Users\aadee\OneDrive\Desktop\Bajaj\.venv\Scripts\python.exe flask_app.py
) else if "%choice%"=="3" (
    echo.
    echo Command Line Interface
    echo Example usage:
    echo python rag_policy_qa.py --policy "./Sample data/EDLHLGA23009V012223.pdf" --query "your question here"
    echo.
    pause
) else if "%choice%"=="4" (
    echo Goodbye!
    exit
) else (
    echo Invalid choice. Please run the script again.
    pause
)

pause
