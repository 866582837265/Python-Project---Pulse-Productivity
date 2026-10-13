@echo off
echo Starting Pulse Productivity App...

echo Starting Backend...
start cmd /k "cd backend && python app.py"

timeout /t 3 /nobreak >nul

echo Starting Frontend...
start cmd /k "cd frontend && npm run dev"

echo Both services started!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
pause