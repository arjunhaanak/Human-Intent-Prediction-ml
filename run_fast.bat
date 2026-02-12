@echo off
echo ===================================================
echo   LIGHTWEIGHT SETUP - Human Intent Prediction
echo ===================================================

:: 1. Force kill any existing python processes that might be locking folders
taskkill /F /IM python.exe /T >nul 2>&1

:: 2. Create environment WITHOUT pip first (this is much faster and more stable)
echo [1/3] Creating environment base...
if exist env_fast (
    echo Found existing env_fast, reusing...
) else (
    py -3.12 -m venv env_fast --without-pip
)

:: 3. Manually get pip in there
echo [2/3] Installing/Updating dependencies...
py -3.12 -m pip install -r requirements.txt --target env_fast\Lib\site-packages

:: 4. Attempt to run using the 3.12 runner directly
echo [3/3] Starting App...
py -3.12 -m streamlit run app.py
pause
