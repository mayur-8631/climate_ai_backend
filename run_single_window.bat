@echo off
echo ========================================================
echo   ClimateTwin AI - Launching Full Platform (Single Window)
echo   Backend: FastAPI (Port 8000)
echo   Frontend: Next.js (Port 3000)
echo ========================================================
echo.

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start /b python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

timeout /t 3 /nobreak >nul

echo [2/2] Starting Next.js Frontend on http://localhost:3000 ...
cd frontend
npm run dev

