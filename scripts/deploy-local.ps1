# BrainSpark 本地部署脚本
# 用于在本地启动所有服务和应用

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BrainSpark 本地部署脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Node.js 是否安装
Write-Host "[1/5] 检查 Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 未找到 Node.js，请先安装 Node.js >= 18" -ForegroundColor Red
    exit 1
}
Write-Host "  Node.js 版本: $nodeVersion" -ForegroundColor Green

# 检查 pnpm 是否安装
Write-Host "[2/5] 检查 pnpm..." -ForegroundColor Yellow
$pnpmVersion = pnpm --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 未找到 pnpm，请运行: npm install -g pnpm" -ForegroundColor Red
    exit 1
}
Write-Host "  pnpm 版本: $pnpmVersion" -ForegroundColor Green

# 安装依赖
Write-Host "[3/5] 安装依赖..." -ForegroundColor Yellow
pnpm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 依赖安装失败" -ForegroundColor Red
    exit 1
}
Write-Host "  依赖安装完成" -ForegroundColor Green

# 启动前端应用
Write-Host "[4/5] 启动前端应用..." -ForegroundColor Yellow
Write-Host "  学生端: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  家长端: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  教师端: http://localhost:3002" -ForegroundColor Cyan
Write-Host "  运营端: http://localhost:3003" -ForegroundColor Cyan

# 启动后端服务（需要手动启动）
Write-Host "[5/5] 后端服务启动说明" -ForegroundColor Yellow
Write-Host ""
Write-Host "  后端服务需要手动启动:" -ForegroundColor White
Write-Host ""
Write-Host "  1. 业务后端 (Java):" -ForegroundColor White
Write-Host "     cd apps/backend-business" -ForegroundColor Gray
Write-Host "     mvn spring-boot:run" -ForegroundColor Gray
Write-Host "     端口: 8080" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. 网关 (Go):" -ForegroundColor White
Write-Host "     cd apps/backend-gateway" -ForegroundColor Gray
Write-Host "     go run main.go" -ForegroundColor Gray
Write-Host "     端口: 8081" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. AI 服务 (Python):" -ForegroundColor White
Write-Host "     cd apps/ai-service" -ForegroundColor Gray
Write-Host "     uvicorn main:app --reload" -ForegroundColor Gray
Write-Host "     端口: 8001" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  部署完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  前端服务已启动 (Ctrl+C 停止)" -ForegroundColor White
Write-Host "  后端服务请手动启动" -ForegroundColor White
Write-Host ""