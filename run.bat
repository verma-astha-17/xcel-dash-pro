@echo off
REM Quick Start Guide for AI Use Case Portfolio Dashboard (Windows)

echo ================================
echo AI Use Case Portfolio Dashboard
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo OK: Python found
echo.

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed. Please install pip first.
    pause
    exit /b 1
)

echo OK: pip found
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo OK: Dependencies installed successfully!
echo.
echo Starting Streamlit app...
echo.

streamlit run app.py
pause
