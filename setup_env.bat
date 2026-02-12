@echo off
echo ===================================================
echo Setting up Human Intent Prediction Environment
echo Using Python 3.12 (Stable)
echo ===================================================

:: 1. Create Virtual Environment (using a new name to avoid locks)
echo [1/4] Creating virtual environment 'py312_env'...
py -3.12 -m venv py312_env
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment. 
    echo Please ensure Python 3.12 is installed correctly.
    pause
    exit /b %errorlevel%
)

:: 2. Activate Virtual Environment
echo [2/4] Activating virtual environment...
call py312_env\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b %errorlevel%
)

:: 3. Install Dependencies
echo [3/4] Installing dependencies (this may take a few minutes)...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b %errorlevel%
)

:: 4. Run Application
echo [4/4] Launching Application...
echo ===================================================
echo Success! The app is starting...
echo Please wait for the browser to open.
echo ===================================================
streamlit run app.py
pause
