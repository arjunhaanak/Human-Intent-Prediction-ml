@echo off
echo ===================================================
echo   VERBOSE SETUP - Human Intent Prediction
echo ===================================================

:: 1. Clear any stuck tasks
taskkill /F /IM python.exe /T >nul 2>&1

:: 2. Install dependencies directly to a local folder with PROGRESS shown
echo [1/2] Installing Dependencies (Showing Progress)...
echo ---------------------------------------------------
echo NOTE: This will download about 1.5 GB of AI models.
echo If the text stops moving for a minute, it is just 
echo downloading a large file. PLEASE STAY PATIENT.
echo ---------------------------------------------------
echo.

py -3.12 -m pip install --progress-bar on -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installation failed. Try running:
    echo py -3.12 -m pip install streamlit torch transformers opencv-python librosa
    pause
    exit /b
)

:: 3. Run the app
echo.
echo [2/2] Launching Application...
py -3.12 -m streamlit run app.py
pause
