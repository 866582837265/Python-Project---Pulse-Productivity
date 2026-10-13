@echo off
echo Starting Pulse Backend Server...
echo ================================

cd /d "%~dp0backend"

echo Setting environment variables...
set FLASK_DEBUG=True
set FLASK_ENV=development

echo Starting Flask server on http://127.0.0.1:5000...
python app.py

pause