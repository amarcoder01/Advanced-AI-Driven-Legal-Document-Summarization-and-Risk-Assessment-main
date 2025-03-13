@echo off
echo Stopping any existing Streamlit processes...
taskkill /f /im streamlit.exe >nul 2>&1

echo Starting AI Legal Document Assistant...
streamlit run app.py

echo If you encounter any issues, run this batch file again.
pause
