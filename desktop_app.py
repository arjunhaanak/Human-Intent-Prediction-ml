import webview
import threading
import subprocess
import time
import os
import sys

def start_streamlit():
    """Start the Streamlit server as a subprocess."""
    # Use the current python executable to run streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true", "--server.port", "8501"]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    # 1. Start Streamlit in the background
    print("🚀 Initializing Neural Intent Core Desktop Engine...")
    thread = threading.Thread(target=start_streamlit, daemon=True)
    thread.start()

    # 2. Wait for server to initialize
    print("📡 Synchronizing with local neural node...")
    time.sleep(5) 

    # 3. Create a high-end native window
    # Note: Using pywebview (pip install pywebview)
    try:
        window = webview.create_window(
            'NEURAL INTENT CORE | Desktop Suite', 
            'http://localhost:8501',
            width=1280,
            height=850,
            background_color='#020617',
            resizable=True
        )
        webview.start(debug=False)
    except Exception as e:
        print(f"❌ Desktop transition failed: {e}")
        print("💡 Falling back to browser mode...")
        # Fallback to just opening in browser if webview fails
        import webbrowser
        webbrowser.open('http://localhost:8501')

if __name__ == "__main__":
    main()
