@echo off
setlocal EnableDelayedExpansion

echo 🚀 Starting Faker Agent Development Environment...

:: Set title
title Faker Agent Development Environment

:: Define service ports
set BACKEND_PORT=8000
set FRONTEND_PORT=5173

:: Check and terminate existing services
echo 🔍 Checking for existing services...
echo.

:: Function to check if port is in use
:check_port_in_use
set PORT=%~1
set SERVICE_NAME=%~2
set PID_LIST=

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT% ^| findstr LISTENING') do (
    set PID_LIST=!PID_LIST! %%a
)

if defined PID_LIST (
    echo ⚠️  Found running %SERVICE_NAME% on port %PORT%, terminating PIDs:%PID_LIST%
    
    for %%p in (!PID_LIST!) do (
        echo    Stopping PID: %%p
        taskkill /f /pid %%p 2>nul
        
        :: Verify termination
        timeout /t 1 /nobreak >nul
        tasklist | findstr /i "%%p" >nul
        if not errorlevel 1 (
            echo    Retry terminating PID: %%p
            taskkill /f /pid %%p 2>nul
            timeout /t 2 /nobreak >nul
        )
    )
    
    :: Final verification
    set STILL_RUNNING=
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT% ^| findstr LISTENING') do (
        set STILL_RUNNING=1
    )
    
    if defined STILL_RUNNING (
        echo ❌ Unable to terminate all processes on port %PORT%
        echo    Please manually close applications using port %PORT% before continuing
        choice /c YN /m "Do you want to continue anyway?"
        if errorlevel 2 exit /b
    ) else (
        echo ✅ %SERVICE_NAME% terminated successfully
    )
) else (
    echo ✓ No %SERVICE_NAME% detected on port %PORT%
)

goto :eof

:: Main execution
:: Check for backend services
call :check_port_in_use %BACKEND_PORT% "backend service"

:: Check for frontend services
call :check_port_in_use %FRONTEND_PORT% "frontend service"

echo ✅ Service check completed
echo.

:: Start backend service
echo 🔧 Starting backend service...
cd backend
start "Backend Service [PORT:%BACKEND_PORT%]" /D "%cd%" cmd /k "uvicorn main:app --reload"
cd ..

:: Verify backend service started
echo    Waiting for backend service to start...
set /a RETRY=0
:retry_backend
timeout /t 2 /nobreak >nul
curl -s -o nul -w "%%{http_code}" http://localhost:%BACKEND_PORT% >nul 2>&1
if not %errorlevel% equ 0 (
    set /a RETRY+=1
    if %RETRY% lss 5 (
        echo    Retry %RETRY%/5: Backend not responding yet...
        goto retry_backend
    ) else (
        echo ⚠️  Backend service might not have started properly
    )
) else (
    echo ✅ Backend service started successfully
)

:: Start frontend service
echo 🌐 Starting frontend service with hot reload...
cd frontend
start "Frontend Service [PORT:%FRONTEND_PORT% - Hot Reload Enabled]" /D "%cd%" cmd /k "npm run dev -- --host 0.0.0.0 --port %FRONTEND_PORT% --strictPort --clearScreen false"
cd ..

:: Verify frontend service started
echo    Waiting for frontend service to start...
set /a RETRY=0
:retry_frontend
timeout /t 2 /nobreak >nul
curl -s -o nul -w "%%{http_code}" http://localhost:%FRONTEND_PORT% >nul 2>&1
if not %errorlevel% equ 0 (
    set /a RETRY+=1
    if %RETRY% lss 10 (
        echo    Retry %RETRY%/10: Frontend not responding yet...
        goto retry_frontend
    ) else (
        echo ⚠️  Frontend service might not have started properly
    )
) else (
    echo ✅ Frontend service started successfully
)

echo.
echo 🎉 Development environment startup completed!
echo    Backend API: http://localhost:%BACKEND_PORT%
echo    API Docs: http://localhost:%BACKEND_PORT%/docs
echo    Frontend: http://localhost:%FRONTEND_PORT%
echo.
echo 🛑 To stop all services:
echo    1. Press Ctrl+C in this window, or
echo    2. Close the command windows directly
echo.
echo 🔄 To restart services, run this script again
echo.

pause