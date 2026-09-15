@echo off
title ArtisanAI Enhanced Prototype
cd /d "%~dp0"
echo.
echo  ============================================
echo   ArtisanAI - Enhanced Prototype
echo   AI Studio + Voice Catalog + Smart Pricing
echo  ============================================
echo.
echo  Installing / checking dependencies...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
  echo ERROR: Python / pip not found. Install Python 3.10+ from python.org
  echo Make sure "Add Python to PATH" is checked.
  pause
  exit /b 1
)
echo.
echo  Starting server...
echo  Open in any browser:  http://127.0.0.1:5000
echo  Press Ctrl+C to stop.
echo.
python app.py
pause
