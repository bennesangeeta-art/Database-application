@echo off
cd /d "%~dp0\backend"
echo Starting PRODUCTION backend server with Waitress...
python run_production.py
pause
