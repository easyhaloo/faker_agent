#!/bin/bash

# 启动后端和前端开发服务器的一键脚本（带服务检测和自动清理功能）

echo "🚀 启动 Faker Agent 开发环境..."

# 定义服务端口
BACKEND_PORT=8000
FRONTEND_PORT=5173

# 检测并终止已存在的服务
kill_existing_services() {
    echo "🔍 检测已存在的服务..."
    
    # 检测并终止指定端口的服务
    kill_service_on_port() {
        local PORT=$1
        local SERVICE_NAME=$2
        local MAX_RETRIES=3
        local RETRY_COUNT=0
        
        # 检测服务
        local PIDS=$(lsof -ti:$PORT)
        
        if [[ -n "$PIDS" ]]; then
            echo "⚠️  发现运行中的$SERVICE_NAME (端口: $PORT, PID: $PIDS)，正在终止..."
            
            # 尝试正常终止
            kill $PIDS 2>/dev/null
            sleep 1
            
            # 检查是否仍在运行
            PIDS=$(lsof -ti:$PORT)
            if [[ -n "$PIDS" ]]; then
                echo "   进程仍在运行，尝试强制终止..."
                kill -9 $PIDS 2>/dev/null
                sleep 2
            fi
            
            # 重试终止顽固进程
            while [[ -n "$(lsof -ti:$PORT)" && $RETRY_COUNT -lt $MAX_RETRIES ]]; do
                RETRY_COUNT=$((RETRY_COUNT + 1))
                echo "   重试 $RETRY_COUNT/$MAX_RETRIES: 终止端口 $PORT 上的进程..."
                kill -9 $(lsof -ti:$PORT) 2>/dev/null
                sleep 2
            done
            
            # 最终检查
            if [[ -z "$(lsof -ti:$PORT)" ]]; then
                echo "✅ $SERVICE_NAME 已成功终止"
            else
                echo "❌ 无法终止 $SERVICE_NAME，请手动检查端口 $PORT"
                read -p "   是否继续? (y/n): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    echo "退出脚本"
                    exit 1
                fi
            fi
        else
            echo "✓ 未发现 $SERVICE_NAME (端口: $PORT)"
        fi
    }
    
    # 检测并终止后端服务
    kill_service_on_port $BACKEND_PORT "后端服务"
    
    # 检测并终止前端服务
    kill_service_on_port $FRONTEND_PORT "前端服务"
    
    echo "✅ 服务检测和清理完成"
}

# 后端服务启动函数
start_backend() {
    echo "🔧 启动后端服务..."
    cd backend
    uvicorn main:app --reload &
    BACKEND_PID=$!
    cd ..
    
    # 验证服务是否成功启动
    echo "   等待后端服务启动..."
    MAX_RETRIES=10
    RETRY_COUNT=0
    
    while [[ $RETRY_COUNT -lt $MAX_RETRIES ]]; do
        sleep 2
        if curl -s http://localhost:$BACKEND_PORT/ > /dev/null 2>&1; then
            echo "✅ 后端服务已成功启动 (PID: $BACKEND_PID)"
            echo "   后端地址: http://localhost:$BACKEND_PORT"
            echo "   API文档: http://localhost:$BACKEND_PORT/docs"
            return 0
        fi
        
        # 检查进程是否还在运行
        if ! ps -p $BACKEND_PID > /dev/null; then
            echo "❌ 后端服务启动失败，进程已终止"
            return 1
        fi
        
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "   重试 $RETRY_COUNT/$MAX_RETRIES: 后端服务尚未响应..."
    done
    
    echo "⚠️  后端服务可能未正确启动，但进程仍在运行 (PID: $BACKEND_PID)"
    echo "   请检查日志获取更多信息"
    return 0
}

# 前端服务启动函数
start_frontend() {
    echo "🌐 启动前端服务..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    # 验证服务是否成功启动
    echo "   等待前端服务启动..."
    MAX_RETRIES=15
    RETRY_COUNT=0
    
    while [[ $RETRY_COUNT -lt $MAX_RETRIES ]]; do
        sleep 2
        if curl -s http://localhost:$FRONTEND_PORT/ > /dev/null 2>&1; then
            echo "✅ 前端服务已成功启动 (PID: $FRONTEND_PID)"
            echo "   前端地址: http://localhost:$FRONTEND_PORT"
            return 0
        fi
        
        # 检查进程是否还在运行
        if ! ps -p $FRONTEND_PID > /dev/null; then
            echo "❌ 前端服务启动失败，进程已终止"
            return 1
        fi
        
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "   重试 $RETRY_COUNT/$MAX_RETRIES: 前端服务尚未响应..."
    done
    
    echo "⚠️  前端服务可能未正确启动，但进程仍在运行 (PID: $FRONTEND_PID)"
    echo "   请检查日志获取更多信息"
    return 0
}

# 优雅关闭函数
cleanup() {
    echo -e "\n🛑 正在停止所有服务..."
    
    # 停止后端服务
    if [[ -n $BACKEND_PID ]]; then
        if ps -p $BACKEND_PID > /dev/null; then
            echo "   停止后端服务 (PID: $BACKEND_PID)..."
            kill $BACKEND_PID 2>/dev/null
            
            # 等待进程结束
            WAIT_COUNT=0
            while ps -p $BACKEND_PID > /dev/null && [[ $WAIT_COUNT -lt 5 ]]; do
                sleep 1
                WAIT_COUNT=$((WAIT_COUNT + 1))
            done
            
            # 如果仍在运行，强制终止
            if ps -p $BACKEND_PID > /dev/null; then
                echo "   强制终止后端服务..."
                kill -9 $BACKEND_PID 2>/dev/null
            fi
            
            echo "✅ 后端服务已停止"
        else
            echo "✓ 后端服务已不在运行"
        fi
    fi
    
    # 停止前端服务
    if [[ -n $FRONTEND_PID ]]; then
        if ps -p $FRONTEND_PID > /dev/null; then
            echo "   停止前端服务 (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID 2>/dev/null
            
            # 等待进程结束
            WAIT_COUNT=0
            while ps -p $FRONTEND_PID > /dev/null && [[ $WAIT_COUNT -lt 5 ]]; do
                sleep 1
                WAIT_COUNT=$((WAIT_COUNT + 1))
            done
            
            # 如果仍在运行，强制终止
            if ps -p $FRONTEND_PID > /dev/null; then
                echo "   强制终止前端服务..."
                kill -9 $FRONTEND_PID 2>/dev/null
            fi
            
            echo "✅ 前端服务已停止"
        else
            echo "✓ 前端服务已不在运行"
        fi
    fi
    
    # 确保所有相关端口都已释放
    if [[ -n "$(lsof -ti:$BACKEND_PORT)" ]]; then
        echo "   清理残留的后端端口占用..."
        kill -9 $(lsof -ti:$BACKEND_PORT) 2>/dev/null
    fi
    
    if [[ -n "$(lsof -ti:$FRONTEND_PORT)" ]]; then
        echo "   清理残留的前端端口占用..."
        kill -9 $(lsof -ti:$FRONTEND_PORT) 2>/dev/null
    fi
    
    echo "✅ 所有服务已停止"
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
echo "   后端 API: http://localhost:$BACKEND_PORT"
echo "   API文档: http://localhost:$BACKEND_PORT/docs"
echo "   前端页面: http://localhost:$FRONTEND_PORT"
echo "   按 Ctrl+C 停止所有服务"
echo "   如遇问题，请检查后端和前端的命令窗口日志"

# 等待任意进程结束
wait