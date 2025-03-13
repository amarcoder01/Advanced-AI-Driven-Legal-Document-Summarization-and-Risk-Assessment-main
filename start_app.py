"""
Streamlit Application Launcher
This script safely starts the AI Legal Document Assistant by:
1. Terminating any existing Streamlit processes
2. Starting the app on a specified port
"""

import os
import subprocess
import time
import sys

def kill_existing_streamlit():
    """Kill any existing Streamlit processes to free up ports"""
    print("Clearing existing Streamlit processes...")
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/F', '/IM', 'streamlit.exe'], 
                          stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        else:  # Unix/Linux/MacOS
            subprocess.run(['pkill', '-f', 'streamlit'], 
                          stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        print("Waiting for ports to be released...")
        time.sleep(2)  # Give time for ports to be released
    except Exception as e:
        print(f"Note: {e}")

def start_streamlit(port=8503):
    """Start the Streamlit application on the specified port"""
    try:
        print(f"Starting AI Legal Document Assistant on port {port}...")
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py', 
                      f'--server.port={port}'])
    except Exception as e:
        print(f"Error starting Streamlit: {e}")
        return False
    return True

if __name__ == "__main__":
    # Set custom port to avoid conflicts
    port = 8503
    
    # Kill existing processes
    kill_existing_streamlit()
    
    # Start the application
    start_streamlit(port)
