# BrainSpark 后端服务 Docker 镜像
# 基于 Python 3.11 slim 镜像

# ===== 构建阶段 =====
FROM python:3.11-slim AS builder

WORKDIR /app

# 安装 Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# 复制依赖文件
COPY pyproject.toml poetry.lock* ./

# 导出 requirements.txt（不包含 dev 依赖）
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# ===== 生产镜像 =====
FROM python:3.11-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从 builder 阶段复制 requirements.txt 并安装依赖
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 仅复制应用代码（排除非运行时文件）
COPY app/ ./app/
COPY main.py .
COPY alembic.ini .
COPY alembic/ ./alembic/

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]