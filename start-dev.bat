@echo off
chcp 65001 >nul
title BrainSpark 开发环境启动器

echo ========================================
echo   BrainSpark 开发环境启动器
echo ========================================
echo.

:: 检查 Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)
echo [OK] Node.js 已安装

:: 检查 pnpm
where pnpm >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 pnpm，正在安装...
    npm install -g pnpm
)
echo [OK] pnpm 已安装

:: 安装依赖
echo.
echo [步骤 1/4] 安装项目依赖...
call pnpm install --no-frozen-lockfile
if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [OK] 依赖安装完成

:: 构建共享包
echo.
echo [步骤 2/4] 构建共享包...
call pnpm --filter @brainspark/shared-types build
if %errorlevel% neq 0 (
    echo [警告] shared-types 构建失败，继续启动...
)
echo [OK] 共享包构建完成

:: 启动 Docker 数据库（可选）
echo.
echo [步骤 3/4] 检查 Docker 数据库...
where docker >nul 2>&1
if %errorlevel% equ 0 (
    echo [信息] Docker 已安装，正在启动数据库服务...
    start cmd /c "docker-compose up -d mysql redis mongodb 2>nul"
    echo [OK] 数据库服务已启动
) else (
    echo [信息] Docker 未安装，跳过数据库启动
    echo [信息] 前端将在无后端 API 模式下运行
)

:: 启动前端应用
echo.
echo [步骤 4/4] 启动前端应用...
echo.

:: 教师端 - 端口 3002
echo 启动教师端 (http://localhost:3002)...
start "BrainSpark-Teacher" cmd /c "cd /d %~dp0 && pnpm --filter @brainspark/teacher-web dev"

:: 家长端 - 端口 5173
echo 启动家长端 (http://localhost:5173)...
start "BrainSpark-Parent" cmd /c "cd /d %~dp0 && pnpm --filter @brainspark/parent-web dev"

:: 学生端 - 端口 3000
echo 启动学生端 (http://localhost:3000)...
start "BrainSpark-Student" cmd /c "cd /d %~dp0 && pnpm --filter @brainspark/student-web dev"

:: 运营端 - 端口 5174
echo 启动运营端 (http://localhost:5174)...
start "BrainSpark-Operator" cmd /c "cd /d %~dp0 && pnpm --filter @brainspark/operator-web dev"

echo.
echo ========================================
echo   BrainSpark 开发环境已启动！
echo ========================================
echo.
echo  教师端: http://localhost:3002
echo  家长端: http://localhost:5173
echo  学生端: http://localhost:3000
echo  运营端: http://localhost:5174
echo.
echo  按任意键关闭此窗口（前端将继续运行）
echo ========================================
pause >nul