@echo off
echo ========================================================
echo   ClimateTwin AI - Launching Full Platform MVP
echo   Backend: FastAPI (Port 8000)
echo   Frontend: Next.js (Port 3000)
echo ========================================================
echo.

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "ClimateTwin Backend (FastAPI)" cmd /k "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Next.js Frontend on http://localhost:3000 ...
start "ClimateTwin Frontend (Next.js)" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo   Both services are launching in separate windows!
echo   - Backend Swagger Docs: http://127.0.0.1:8000/docs
echo   - Frontend Dashboard:   http://localhost:3000
echo ========================================================
pause

