@echo off
setlocal EnableDelayedExpansion

echo 🚀 启动 Faker Agent 开发环境...

:: 设置标题
title Faker Agent 开发环境

:: 检测并终止已存在的服务
echo 🔍 检测已存在的服务...
echo.

:: 检查并终止可能正在运行的后端服务 (端口 8000)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo ⚠️  发现运行中的后端服务，正在终止 PID %%a...
    taskkill /f /pid %%a 2>nul
)

:: 检查并终止可能正在运行的前端服务 (端口 5173)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
    echo ⚠️  发现运行中的前端服务，正在终止 PID %%a...
    taskkill /f /pid %%a 2>nul
)

echo ✅ 已清理完所有旧服务
echo.

:: 启动后端服务
echo 🔧 启动后端服务...
cd backend
start "后端服务" /D "%cd%" cmd /k "uvicorn main:app --reload"
cd ..

:: 启动前端服务
echo 🌐 启动前端服务...
cd frontend
start "前端服务" /D "%cd%" cmd /k "npm run dev"
cd ..

echo.
echo 🎉 开发环境启动命令已执行!
echo    后端 API: http://localhost:8000
echo    前端页面: http://localhost:5173
echo    请稍等服务完全启动后再访问
echo.
echo 🛑 要停止服务，请手动关闭对应的命令行窗口
echo.

pause