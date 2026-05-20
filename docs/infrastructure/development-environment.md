# BrainSpark 开发环境设计

> 本文档详细描述 BrainSpark 项目的开发环境配置方案，包括本地开发环境、容器化开发环境、多语言工具链配置和开发工作流。

## 1. 开发环境架构总览

```
┌─────────────────────────────────────────────────────────────────────┐
│                        开发者工作站                                   │
│                                                                     │
│  ┌───────────────────── 本地服务 ──────────────────────┐            │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │            │
│  │  │Student   │  │Parent    │  │Teacher   │         │            │
│  │  │Web:5173  │  │Web:5174  │  │Web:5175  │         │            │
│  │  └──────────┘  └──────────┘  └──────────┘         │            │
│  │  ┌──────────┐  ┌──────────┐                       │            │
│  │  │Business  │  │Gateway   │                       │            │
│  │  │Backend:8081│ │Gateway:8082│                     │            │
│  │  └──────────┘  └──────────┘                       │            │
│  │  ┌──────────┐                                     │            │
│  │  │AI       │                                     │            │
│  │  │Service:8000│                                    │            │
│  │  └──────────┘                                     │            │
│  └───────────────────────────────────────────────────┘            │
│                                                                     │
│  ┌─────────────────── 容器化依赖服务 ───────────────────┐          │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │            │
│  │  │MySQL   │  │Redis     │  │MongoDB   │         │            │
│  │  │:3306   │  │:6379     │  │:27017    │         │            │
│  │  └──────────┘  └──────────┘  └──────────┘         │            │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │            │
│  │  │Kafka   │  │ClickHouse│  │Milvus    │         │            │
│  │  │:9092   │  │:8123     │  │:19530    │         │            │
│  │  └──────────┘  └──────────┘  └──────────┘         │            │
│  └───────────────────────────────────────────────────┘            │
│                                                                     │
│  ┌─────────────────── 开发工具链 ─────────────────────┐           │
│  │  VS Code + ESLint + Prettier + Jest + Vitest      │            │
│  │  Maven + Go Tools + Python venv                    │            │
│  └───────────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. 环境准备清单

### 2.1 系统要求

| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| 操作系统 | Windows 11 / macOS 13+ / Ubuntu 22.04+ | Ubuntu 24.04 / macOS Sonoma |
| CPU | 8 核 | 16 核+ |
| 内存 | 16 GB | 32 GB+ |
| 磁盘 | 50 GB 可用空间 | 100 GB SSD |
| 网络 | 稳定互联网连接 | 国内镜像源加速 |

### 2.2 必需工具链

#### 2.2.1 通用工具

| 工具 | 版本 | 用途 | 安装方式 |
|------|------|------|---------|
| Node.js | 20 LTS | 前端构建、pnpm 运行环境 | [nvm](https://github.com/nvm-sh/nvm) 或直接安装 |
| pnpm | >= 8.0 | 包管理 | `corepack enable` |
| Git | >= 2.40 | 版本控制 | 系统包管理器 |
| Docker | >= 24.0 | 容器化开发依赖 | [Docker Desktop](https://www.docker.com/) |
| Docker Compose | >= 2.20 | 多容器编排 | Docker Desktop 内置 |

#### 2.2.2 前端开发工具

| 工具 | 版本 | 用途 |
|------|------|------|
| Vue DevTools | >= 7.0 | Vue 3 调试 |
| ESLint | >= 8.0 | 代码规范检查 |
| Vite | >= 5.0 | 开发服务器和构建 |

#### 2.2.3 Java 后端工具

| 工具 | 版本 | 用途 |
|------|------|------|
| JDK | 17 (LTS) | Spring Boot 运行环境 |
| Maven | >= 3.9 | 依赖管理和构建 |
| Lombok 插件 | 最新 | IDE Lombok 支持 |

#### 2.2.4 Go 网关工具

| 工具 | 版本 | 用途 |
|------|------|------|
| Go | >= 1.21 | Gin 框架运行环境 |
| goctl / other | - | Go 代码生成工具（可选） |

#### 2.2.5 AI 服务工具

| 工具 | 版本 | 用途 |
|------|------|------|
| Python | >= 3.11 | FastAPI 运行环境 |
| pip / uv | 最新 | 依赖管理 |
| venv / conda | - | 虚拟环境 |

### 2.3 IDE 推荐配置

推荐使用 **VS Code** 作为统一开发工具，安装以下扩展：

| 扩展 | 用途 |
|------|------|
| Vue - Official | Vue 3 语言支持和 IntelliSense |
| TypeScript Vue Plugin | TypeScript 对 `.vue` 文件支持 |
| ESLint | 实时代码规范检查 |
| Prettier | 代码格式化 |
| Go | Go 语言支持 |
| Java Extension Pack | Java 开发支持 |
| Python | Python 开发支持 |
| Docker | Docker 容器管理 |
| GitHub Copilot | AI 辅助编程（可选） |

## 3. 本地开发环境配置

### 3.1 项目初始化

```bash
# 1. 克隆项目
git clone https://github.com/your-org/BrainSpark.git
cd BrainSpark

# 2. 安装全局依赖
corepack enable

# 3. 安装项目依赖
pnpm install

# 4. 创建环境配置文件
cp apps/student-web/.env.example apps/student-web/.env.local
cp apps/backend-business/src/main/resources/application-dev.yml.template apps/backend-business/src/main/resources/application-dev.yml
```

### 3.2 环境变量配置

#### 3.2.1 前端环境变量 (`apps/*/`)

```env
# VITE_API_BASE_URL=http://localhost:8082/api/v1
# VITE_WS_URL=ws://localhost:8082
# VITE_APP_TITLE=BrainSpark Student
```

#### 3.2.2 Java 后端环境变量 (`apps/backend-business/`)

```yaml
# application-dev.yml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/brainspark_dev?useSSL=false&serverTimezone=UTC
    username: root
    password: devpassword
  redis:
    host: localhost
    port: 6379
  rabbitmq:  # 可选
    host: localhost

ai:
  api_key: your_api_key_here
  base_url: https://api.openai.com/v1
```

#### 3.2.3 Go 网关环境变量 (`apps/backend-gateway/`)

```env
GIN_MODE=debug
PORT=8082
BACKEND_BUSINESS_URL=http://localhost:8081
LOG_LEVEL=debug
```

#### 3.2.4 Python AI 服务环境变量 (`apps/ai-service/`)

```env
# .env
AI_PROVIDER=qwen
API_KEY=your_api_key_here
VECTOR_STORE=milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
LOG_LEVEL=DEBUG
```

### 3.3 启动开发服务

#### 3.3.1 使用 Turbo 启动全部

```bash
# 启动所有开发服务
pnpm dev:all
```

#### 3.3.2 单独启动各服务

```bash
# 学生端前端
pnpm dev:student

# 家长端前端
pnpm dev:parent

# 教师端前端
pnpm dev:teacher

# Java 业务后端
cd apps/backend-business && mvn spring-boot:run

# Go 网关
cd apps/backend-gateway && go run main.go

# AI 服务
cd apps/ai-service && uvicorn app.main:app --reload --port 8000
```

## 4. Docker Compose 容器化开发环境

### 4.1 目录结构

```
infra/docker/
├── docker-compose.yml          # 主配置文件
├── docker-compose.dev.yml       # 开发环境扩展配置
├── docker-compose.services.yml  # 基础设施服务配置
├── mysql/
│   ├── Dockerfile
│   ├── init.sql                 # 数据库初始化脚本
│   └── conf.d/
│       └── dev.cnf              # 开发环境 MySQL 配置
├── redis/
│   └── dev.conf                 # 开发环境 Redis 配置
├── kafka/
│   └── kafka.env                # Kafka 环境变量
├── clickhouse/
│   ├── Dockerfile
│   └── init.sql                 # 初始化脚本
├── milvus/
│   └── etcd-config.yaml         # Milvus 依赖配置
└── nginx/
    ├── dev.conf                 # 开发环境反向代理配置
    └── ssl/                     # 开发证书（可选）
```

### 4.2 Docker Compose 主配置

```yaml
# infra/docker/docker-compose.yml
version: '3.8'

x-common-vars: &common-vars
  MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-devpassword}
  MYSQL_DATABASE: ${MYSQL_DATABASE:-brainspark_dev}
  REDIS_PASSWORD: ${REDIS_PASSWORD:-devredis}
  ELASTICSEARCH_PASSWORD: ${ELASTICSEARCH_PASSWORD:-develastic}

services:
  # ============ 数据库服务 ============

  mysql:
    image: mysql:8.0
    container_name: brainspark-mysql-dev
    command: --default-authentication-plugin=caching_sha2_password
    environment:
      <<: *common-vars
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql/init.sql:/docker-entrypoint-initdb.d/01-init.sql
      - ./mysql/conf.d:/etc/mysql/conf.d
    networks:
      - brainspark-dev
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: brainspark-redis-dev
    command: redis-server /usr/local/etc/redis/redis.conf --requirepass ${REDIS_PASSWORD:-devredis}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./redis/dev.conf:/usr/local/etc/redis/redis.conf
    networks:
      - brainspark-dev
    restart: unless-stopped

  mongodb:
    image: mongo:7
    container_name: brainspark-mongo-dev
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-devpassword}
      MONGO_INITDB_DATABASE: brainspark_behavior
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    networks:
      - brainspark-dev
    restart: unless-stopped

  # ============ 消息队列 ============

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: brainspark-kafka-dev
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
    ports:
      - "9092:9092"
    depends_on:
      - zookeeper
    networks:
      - brainspark-dev
    restart: unless-stopped

  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    container_name: brainspark-zookeeper-dev
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"
    networks:
      - brainspark-dev
    restart: unless-stopped

  # ============ 分析存储 ============

  clickhouse:
    image: clickhouse/clickhouse-server:23.8
    container_name: brainspark-clickhouse-dev
    ports:
      - "8123:8123"
      - "9000:9000"
    volumes:
      - clickhouse_data:/var/lib/clickhouse
      - ./clickhouse/init.sql:/docker-entrypoint-initdb.d/01-init.sql
    networks:
      - brainspark-dev
    restart: unless-stopped

  # ============ 向量存储 ============

  milvus:
    image: milvusdb/milvus:v2.4.0
    container_name: brainspark-milvus-dev
    command: ["milvus", "run", "standalone"]
    security_opt:
      - seccomp:unconfined
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
    ports:
      - "19530:19530"
      - "9091:9091"
    depends_on:
      - etcd
      - minio
    networks:
      - brainspark-dev
    restart: unless-stopped

  etcd:
    image: quay.io/coreos/etcd:v3.5.12
    container_name: brainspark-etcd-dev
    command: etcd -name etcd0 -listen-client-urls http://0.0.0.0:2379 -advertise-client-urls http://0.0.0.0:2379
    ports:
      - "2379:2379"
    volumes:
      - etcd_data:/etcd
    networks:
      - brainspark-dev
    restart: unless-stopped

  minio:
    image: minio/minio:latest
    container_name: brainspark-minio-dev
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    networks:
      - brainspark-dev
    restart: unless-stopped

# ============ 数据卷 ============

volumes:
  mysql_data:
  redis_data:
  mongo_data:
  clickhouse_data:
  etcd_data:
  minio_data:

# ============ 网络 ============

networks:
  brainspark-dev:
    driver: bridge
```

### 4.3 启动命令

```bash
# 启动所有基础设施服务
cd infra/docker
docker compose up -d

# 启动指定服务
docker compose up -d mysql redis

# 查看日志
docker compose logs -f mysql

# 停止所有服务
docker compose down

# 停止并删除数据卷（危险操作！）
docker compose down -v
```

## 5. 开发工作流

### 5.1 Git 工作流

本项目采用 [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) 变体工作流：

```
main (生产)
│
├── develop (开发)
│   │
│   ├── feat/user-auth      # 新功能
│   ├── feat/assessment     # 新功能
│   ├── fix/login-bug       # Bug 修复
│   └── refactor/db-config  # 重构
│
└── hotfix/payment-issue    # 紧急修复
```

#### 分支命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 新功能 | `feat/描述` | `feat/schulte-grid` |
| Bug 修复 | `fix/描述` | `fix/token-refresh` |
| 重构 | `refactor/描述` | `refactor/cache-strategy` |
| 文档 | `docs/描述` | `docs/development-env` |
| 构建/工具 | `chore/描述` | `chore/docker-setup` |
| 测试 | `test/描述` | `test/unit-auth` |
| 热修复 | `hotfix/描述` | `hotfix/payment-timeout` |

#### 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```bash
feat(student-web): add Schulte grid game engine
fix(backend-business): resolve token refresh deadlock
refactor(ai-service): optimize RAG retrieval pipeline
docs(architecture): update API contract v1.2
test(assessment): add unit tests for analyzer
chore(deploy): add staging environment config
```

### 5.2 代码质量检查

```bash
# 运行所有检查
pnpm lint:all
pnpm typecheck:all

# 单个服务检查
pnpm --filter @brainspark/student lint
pnpm --filter @brainspark/student type-check

# Java 后端
cd apps/backend-business && mvn checkstyle:check && mvn test

# Go 网关
cd apps/backend-gateway && golangci-lint run ./...

# Python AI 服务
cd apps/ai-service && pip install flake8 && flake8 app/
```

### 5.3 调试配置

#### 5.3.1 VS Code 调试配置 (`.vscode/launch.json`)

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Student Web",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/apps/student-web/src"
    },
    {
      "name": "Debug Java Backend",
      "type": "java",
      "request": "launch",
      "mainClass": "${workspaceFolder}/apps/backend-business/src/main/java/com/brainspark/BrainSparkApplication.java",
      "stopAtEntry": false,
      "args": "--spring.profiles.active=dev"
    },
    {
      "name": "Debug Go Gateway",
      "type": "go",
      "request": "launch",
      "mode": "debug",
      "program": "${workspaceFolder}/apps/backend-gateway/main.go"
    },
    {
      "name": "Debug AI Service",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--port", "8000"],
      "cwd": "${workspaceFolder}/apps/ai-service"
    }
  ]
}
```

#### 5.3.2 VS Code 任务配置 (`.vscode/tasks.json`)

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start All Dev Services",
      "type": "shell",
      "command": "pnpm dev:all",
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      },
      "runOptions": {
        "instanceLimit": 1
      }
    },
    {
      "label": "Start Infrastructure Services",
      "type": "shell",
      "command": "docker compose -f infra/docker/docker-compose.yml up -d",
      "group": "build"
    },
    {
      "label": "Stop Infrastructure Services",
      "type": "shell",
      "command": "docker compose -f infra/docker/docker-compose.yml down",
      "group": "build"
    },
    {
      "label": "Run All Tests",
      "type": "shell",
      "command": "pnpm test:all",
      "group": "test"
    }
  ]
}
```

## 6. 开发工具链配置

### 6.1 Git Hooks (Husky + lint-staged)

```json
// package.json (root)
{
  "scripts": {
    "prepare": "husky install"
  },
  "lint-staged": {
    "*.{vue,ts,js}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.java": [
      "cd apps/backend-business && mvn spotless:apply"
    ],
    "*.go": [
      "gofmt -w",
      "golangci-lint run"
    ],
    "*.py": [
      "flake8 --max-line-length=120"
    ]
  }
}
```

### 6.2 Docker 开发配置

```dockerfile
# apps/student-web/Dockerfile.dev
FROM node:20-alpine AS base
WORKDIR /app
RUN corepack enable

# 依赖安装阶段
FROM base AS deps
COPY package.json pnpm-workspace.yaml ./
COPY packages ./packages
RUN --mount=type=cache,id=pnpm,target=/root/.pnpm-store pnpm install --frozen-lockfile

# 构建阶段
FROM base AS build
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

# 开发服务器
FROM base AS dev
RUN corepack enable pnpm
RUN apk add --no-cache openssl
WORKDIR /app
COPY package.json pnpm-workspace.yaml ./
COPY packages ./packages
RUN --mount=type=cache,id=pnpm,target=/root/.pnpm-store pnpm install
COPY --chown=node:node . .
USER node
EXPOSE 5173
CMD ["pnpm", "dev:student"]
```

## 7. 常见问题排查

### 7.1 端口冲突

```bash
# 查看占用端口的进程
lsof -i :3306  # macOS/Linux
netstat -ano | findstr :3306  # Windows

# 修改 Docker Compose 端口映射
# docker-compose.yml 中修改 "3306:3306" -> "3307:3306"
```

### 7.2 数据库连接问题

```bash
# 检查 MySQL 是否运行
docker ps | grep mysql

# 查看 MySQL 日志
docker logs brainspark-mysql-dev

# 重置数据库
docker compose down -v
docker compose up -d mysql
```

### 7.3 Node.js 依赖问题

```bash
# 清除缓存并重新安装
rm -rf node_modules
rm pnpm-lock.yaml
pnpm install

# 检查 Node 版本
node --version  # 应为 v20.x
```

## 8. 附录：快速启动指南

### 8.1 全新环境首次启动

```bash
# 1. 环境验证
node --version        # v20.x
pnpm --version        # 8.x+
docker --version      # 24.x+
mysql --version       # 8.x+ (用于客户端连接)

# 2. 克隆项目
git clone <repo-url>
cd BrainSpark

# 3. 安装依赖
corepack enable
pnpm install

# 4. 启动基础设施服务
docker compose -f infra/docker/docker-compose.yml up -d

# 5. 初始化数据库（首次运行）
# MySQL 会自动执行 infra/docker/mysql/init.sql

# 6. 配置环境变量
cp apps/student-web/.env.example apps/student-web/.env.local
# 编辑 .env.local 文件

# 7. 启动开发服务
pnpm dev:all

# 8. 验证服务
# - 学生端: http://localhost:5173
# - 家长端: http://localhost:5174
# - 教师端: http://localhost:5175
# - API: http://localhost:8082
# - MySQL: localhost:3306 (root / devpassword)
```

### 8.2 环境验证脚本

```bash
#!/bin/bash
# scripts/verify-environment.sh

echo "=== BrainSpark 开发环境验证 ==="
echo ""

# 检查 Node.js
if command -v node &> /dev/null; then
  echo "✓ Node.js: $(node --version)"
else
  echo "✗ Node.js 未安装"
fi

# 检查 pnpm
if command -v pnpm &> /dev/null; then
  echo "✓ pnpm: $(pnpm --version)"
else
  echo "✗ pnpm 未安装"
fi

# 检查 Docker
if command -v docker &> /dev/null; then
  echo "✓ Docker: $(docker --version)"
else
  echo "✗ Docker 未安装"
fi

# 检查 MySQL 客户端
if command -v mysql &> /dev/null; then
  echo "✓ MySQL 客户端: $(mysql --version)"
else
  echo "- MySQL 客户端未安装（可选）"
fi

echo ""
echo "=== 环境验证完成 ==="
```

---

> 本文档为基础设施目录入口文件，创建于 2026-05-20。