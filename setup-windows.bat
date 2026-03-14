@echo off
REM Automated EDA - Windows Development Setup Script

echo.
echo ===============================================
echo Automated EDA - Development Setup
echo ===============================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed!
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo [1/5] Docker is installed ✓
echo.

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo [2/5] Git is installed ✓
echo.

REM Create environment files if they don't exist
if not exist "server\.env" (
    echo [3/5] Creating server\.env file...
    copy server\.env.example server\.env
    echo Created server\.env - Please edit with your values!
) else (
    echo [3/5] server\.env already exists ✓
)
echo.

if not exist "client\.env" (
    echo [4/5] Creating client\.env file...
    copy client\.env.example client\.env
    echo Created client\.env - Please edit with your values!
) else (
    echo [4/5] client\.env already exists ✓
)
echo.

REM Start Docker Compose in development mode
echo [5/5] Starting Docker services in development mode...
docker-compose -f docker-compose.dev.yml up -d --build

echo.
echo ===============================================
echo Setup Complete!
echo ===============================================
echo.
echo Your application is starting. Please wait 30 seconds for services to be ready...
echo.
echo Access your application at:
echo   Frontend:   http://localhost:3000
echo   API:        http://localhost:8000
echo   API Docs:   http://localhost:8000/docs
echo.
echo Useful commands:
echo   View logs:      docker-compose -f docker-compose.dev.yml logs -f
echo   Stop services:  docker-compose -f docker-compose.dev.yml down
echo   Restart:        docker-compose -f docker-compose.dev.yml restart
echo.
pause
