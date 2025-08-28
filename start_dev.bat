@echo off
setlocal EnableDelayedExpansion

echo 🚀 Starting Faker Agent Development Environment...

:: Set title
title Faker Agent Development Environment

:: Check and terminate existing services
echo 🔍 Checking for existing services...
echo.

:: Check and terminate running backend service (port 8000)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo ⚠️  Found running backend service, terminating PID %%a...
    taskkill /f /pid %%a 2>nul
)

:: Check and terminate running frontend service (port 5173)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
    echo ⚠️  Found running frontend service, terminating PID %%a...
    taskkill /f /pid %%a 2>nul
)

echo ✅ All old services cleaned
echo.

:: Start backend service
echo 🔧 Starting backend service...
cd backend
start "Backend Service" /D "%cd%" cmd /k "uvicorn main:app --reload"
cd ..

:: Start frontend service
echo 🌐 Starting frontend service...
cd frontend
start "Frontend Service" /D "%cd%" cmd /k "npm run dev"
cd ..

echo.
echo 🎉 Development environment startup commands executed!
echo    Backend API: http://localhost:8000
echo    Frontend: http://localhost:5173
echo    Please wait for services to fully start before accessing
echo.
echo 🛑 To stop the services, manually close the corresponding command windows
echo.

pause