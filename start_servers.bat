@echo off
echo ============================================
echo AUTOMATED EDA - START ALL SERVICES
echo ============================================
echo.

echo [1/3] Checking if servers are already running...
netstat -ano | findstr :8000 >nul
if %ERRORLEVEL% EQU 0 (
    echo   Backend already running on port 8000
) else (
    echo   Starting backend server...
    start "Backend Server" /MIN cmd /c "cd /d %~dp0server && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
    timeout /t 5 /nobreak >nul
)

netstat -ano | findstr :5173 >nul
if %ERRORLEVEL% EQU 0 (
    echo   Frontend already running on port 5173
) else (
    echo   Starting frontend server...
    start "Frontend Server" /MIN cmd /c "cd /d %~dp0client && npm run dev"
    timeout /t 5 /nobreak >nul
)

echo.
echo [2/3] Servers starting...
timeout /t 10 /nobreak >nul

echo.
echo [3/3] Opening application in browser...
start http://localhost:5173

echo.
echo ============================================
echo   SERVICES RUNNING:
echo   - Backend:  http://127.0.0.1:8000
echo   - Frontend: http://localhost:5173
echo   - API Docs: http://127.0.0.1:8000/docs
echo ============================================
echo.
echo Press any key to stop all services...
pause >nul

echo Stopping services...
taskkill /FI "WINDOWTITLE eq Backend Server*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend Server*" /F >nul 2>&1
echo Services stopped.
