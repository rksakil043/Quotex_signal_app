@echo off
setlocal
python --version >nul 2>&1 || (
  echo Python is required. Download from https://www.python.org/downloads/
  pause
  exit /b
)
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
pause
