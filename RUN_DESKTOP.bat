@echo off
setlocal
echo 🚀 NEURAL INTENT CORE ^| SYSTEM INITIALIZER
echo ------------------------------------------

:: Check for pywebview dependency
python -c "import webview" 2>nul
if %errorlevel% neq 0 (
    echo 📦 Installing Desktop Engine dependencies...
    pip install pywebview
)

echo 📡 Launching Desktop Suite...
python desktop_app.py
pause
