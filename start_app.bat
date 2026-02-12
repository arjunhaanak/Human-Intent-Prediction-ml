@echo off
echo ===================================================
echo   FINAL SETUP - Human Intent Prediction
echo ===================================================

:: 1. Create a FRESH virtual environment (env_final)
echo [1/3] Creating fresh environment (env_final)...
:: Check if python 3.12 is available
py -3.12 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.12 launcher not found.
    pause
    exit /b
)

:: Create env if not exists
if not exist env_final (
    py -3.12 -m venv env_final
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create environment.
        pause
        exit /b
    )
) else (
    echo Found existing env_final.
)

:: Verify it was created correctly
if not exist env_final\Scripts\python.exe (
    echo [ERROR] Environment broken (python.exe missing).
    echo Deleting and retrying...
    rmdir /s /q env_final
    py -3.12 -m venv env_final
)

:: 2. Upgrade pip and install requirements
echo.
echo [2/3] Installing dependencies...
echo ---------------------------------------------------
echo NOTE: You will see a lot of text scrolling.
echo This is NORMAL. The system is downloading AI models.
echo PLEASE WAIT (5-10 minutes). Do not close the window.
echo ---------------------------------------------------
echo.

env_final\Scripts\python.exe -m pip install --upgrade pip
env_final\Scripts\python.exe -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] installation failed.
    pause
    exit /b
)

:: 3. Run
echo.
echo [3/3] Starting App...
echo Opening browser...
echo.
env_final\Scripts\python.exe -m streamlit run app.py
pause
