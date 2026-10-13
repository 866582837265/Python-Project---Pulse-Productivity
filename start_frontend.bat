@echo off
echo Starting Pulse Frontend...
echo ==========================

cd /d "%~dp0frontend"

echo Installing dependencies (if needed)...
call npm install

echo Starting Vite dev server...
call npm run dev

pause