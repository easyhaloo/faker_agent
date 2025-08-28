#!/bin/bash

# 启动后端和前端开发服务器的一键脚本（带服务检测和自动清理功能）

echo "🚀 启动 Faker Agent 开发环境..."

# 检测并终止已存在的服务
kill_existing_services() {
    echo "🔍 检测已存在的服务..."
    
    # 检测后端服务 (端口 8000)
    BACKEND_PIDS=$(lsof -ti:8000)
    if [[ -n "$BACKEND_PIDS" ]]; then
        echo "⚠️  发现运行中的后端服务 (PID: $BACKEND_PIDS)，正在终止..."
        kill -9 $BACKEND_PIDS 2>/dev/null
        sleep 2
    fi
    
    # 检测前端服务 (端口 5173)
    FRONTEND_PIDS=$(lsof -ti:5173)
    if [[ -n "$FRONTEND_PIDS" ]]; then
        echo "⚠️  发现运行中的前端服务 (PID: $FRONTEND_PIDS)，正在终止..."
        kill -9 $FRONTEND_PIDS 2>/dev/null
        sleep 2
    fi
    
    # 再次检查是否还有残留进程
    BACKEND_PIDS=$(lsof -ti:8000)
    FRONTEND_PIDS=$(lsof -ti:5173)
    
    if [[ -z "$BACKEND_PIDS" && -z "$FRONTEND_PIDS" ]]; then
        echo "✅ 已清理完所有旧服务"
    else
        echo "❌ 无法终止部分服务，请手动检查"
    fi
}

# 后端服务启动函数
start_backend() {
    echo "🔧 启动后端服务..."
    cd backend
    uvicorn main:app --reload &
    BACKEND_PID=$!
    cd ..
    echo "✅ 后端服务已在后台启动 (PID: $BACKEND_PID)"
    echo "   后端地址: http://localhost:8000"
    echo "   API文档: http://localhost:8000/docs"
}

# 前端服务启动函数
start_frontend() {
    echo "🌐 启动前端服务..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    echo "✅ 前端服务已在后台启动 (PID: $FRONTEND_PID)"
    echo "   前端地址: http://localhost:5173"
}

# 优雅关闭函数
cleanup() {
    echo -e "\n🛑 正在停止所有服务..."
    if [[ -n $BACKEND_PID ]]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ 后端服务已停止"
    fi
    
    if [[ -n $FRONTEND_PID ]]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ 前端服务已停止"
    fi
    exit 0
}

# 注册信号处理器
trap cleanup INT TERM

# 先清理已有服务
kill_existing_services

# 启动服务
start_backend
start_frontend

echo -e "\n🎉 开发环境启动完成!"
echo "   后端 API: http://localhost:8000"
echo "   前端页面: http://localhost:5173"
echo "   按 Ctrl+C 停止所有服务"

# 等待任意进程结束
wait