# BrainSpark 安装配置手册

> 本文档提供 BrainSpark 项目开发环境的详细安装和配置步骤，适用于首次开发的团队成员。

## 目录

- [前置条件](#1-前置条件)
- [Step 1: 安装系统依赖](#2-step-1安装系统依赖)
- [Step 2: 克隆项目代码](#3-step-2克隆项目代码)
- [Step 3: 安装项目依赖](#4-step-3安装项目依赖)
- [Step 4: 启动基础设施服务](#5-step-4启动基础设施服务)
- [Step 5: 配置环境变量](#6-step-5配置环境变量)
- [Step 6: 初始化数据库](#7-step-6初始化数据库)
- [Step 7: 启动开发服务](#8-step-7启动开发服务)
- [Step 8: 验证安装](#9-step-8验证安装)
- [常见问题排查](#10-常见问题排查)
- [附录](#11-附录)

---

## 1. 前置条件

在安装前，请确认您的开发机器满足以下要求：

### 1.1 系统要求

| 项目 | 最低配置 | 推荐配置 |
|------|---------|---------|
| 操作系统 | Windows 11 / macOS 13+ / Ubuntu 22.04+ | Ubuntu 24.04 / macOS Sonoma |
| CPU | 8 核 | 16 核+ |
| 内存 | 16 GB | 32 GB+ |
| 磁盘空间 | 50 GB 可用空间 | 100 GB SSD |
| 网络 | 稳定互联网连接 | 国内镜像源加速 |

### 1.2 已安装软件检查

在安装任何新软件前，请先检查以下工具是否已安装：

```bash
# 检查 Git
git --version
# 预期输出: git version x.x.x

# 检查 Docker
docker --version
# 预期输出: Docker version x.x.x

# 检查 Docker Compose
docker compose version
# 预期输出: Docker Compose version x.x.x

# 检查 Node.js
node --version
# 预期输出: v20.x.x

# 检查 pnpm
pnpm --version
# 预期输出: 8.x.x 或更高

# 检查 Java
java -version
# 预期输出: openjdk version "17.x.x"

# 检查 Maven
mvn --version
# 预期输出: Apache Maven 3.9.x

# 检查 Go
go version
# 预期输出: go1.x.x

# 检查 Python
python3 --version
# 预期输出: Python 3.11.x
```

如果有工具未安装，请参考 [Step 1](#2-step-1安装系统依赖) 进行安装。

---

## 2. Step 1: 安装系统依赖

本节详细介绍各工具的安装方法。

### 2.1 安装 Git

#### Windows

1. 访问 [Git for Windows](https://git-scm.com/download/win) 下载最新安装包
2. 运行安装程序，使用默认设置
3. 安装完成后重启终端

#### macOS

```bash
# 使用 Homebrew 安装
brew install git
```

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install git
```

### 2.2 安装 Docker Desktop

#### Windows

1. 确保已启用 WSL 2：
   ```powershell
   # 以管理员身份运行 PowerShell
   wsl --install
   # 重启电脑
   ```
2. 下载 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
3. 运行安装程序并按提示完成

#### macOS

1. 下载 [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
2. 将 Docker.app 拖入 Applications 文件夹
3. 启动 Docker Desktop，完成初始设置

#### Ubuntu/Debian

```bash
# 添加 Docker 官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 添加 Docker 仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 2.3 安装 Node.js 20 LTS

#### 使用 nvm（推荐）

**Windows:**
1. 使用 [nvm-windows](https://github.com/coreybutler/nvm-windows)
2. 安装后执行:
   ```cmd
   nvm install 20
   nvm use 20
   nvm alias default 20
   ```

**macOS/Linux:**
```bash
# 安装 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 重启终端，然后安装 Node.js
nvm install 20
nvm use 20
nvm alias default 20
```

#### 直接安装

访问 [Node.js 官网](https://nodejs.org/) 下载 LTS 版本安装包。

### 2.4 启用 corepack (pnpm)

```bash
# 启用 corepack
corepack enable

# 验证 pnpm 可用
pnpm --version
```

### 2.5 安装 JDK 17

#### Windows

1. 下载 [Eclipse Temurin JDK 17](https://adoptium.net/temurin/releases/?version=17)
2. 运行安装程序
3. 设置环境变量 `JAVA_HOME` 指向安装目录

#### macOS

```bash
# 使用 Homebrew 安装
brew install --cask temurin@17

# 设置 JAVA_HOME
echo 'export JAVA_HOME=$(/usr/libexec/java_home -v 17)' >> ~/.zshrc
source ~/.zshrc
```

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install openjdk-17-jdk

# 验证安装
java -version
```

### 2.6 安装 Maven

#### Windows

1. 下载 [Maven Binary](https://maven.apache.org/download.cgi)
2. 解压到文件夹，如 `C:\Program Files\Apache\maven`
3. 添加环境变量：
   - `MAVEN_HOME = C:\Program Files\Apache\maven`
   - 将 `%MAVEN_HOME%\bin` 添加到 `PATH`

#### macOS

```bash
brew install maven
```

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install maven
```

### 2.7 安装 Go

#### Windows

1. 访问 [Go 官网](https://go.dev/dl/) 下载 Windows 安装包
2. 运行安装程序
3. 验证：`go version`

#### macOS

```bash
brew install go
```

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install golang-go
```

### 2.8 安装 Python 3.11+

Windows/macOS 用户请从 [Python 官网](https://www.python.org/downloads/) 下载安装。

Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2.9 安装 VS Code 推荐扩展

1. 下载并安装 [Visual Studio Code](https://code.visualstudio.com/)
2. 打开 VS Code，打开 BrainSpark 项目
3. 根据提示安装推荐扩展，或手动安装以下扩展：

| 扩展 ID | 名称 | 用途 |
|---------|------|------|
| `Vue.volar` | Vue - Official | Vue 3 语言支持 |
| `dbaeumer.vscode-eslint` | ESLint | 代码检查 |
| `esbenp.prettier-vscode` | Prettier | 代码格式化 |
| `golang.go` | Go | Go 语言支持 |
| `vscjava.vscode-java-pack` | Java Extension Pack | Java 开发支持 |
| `ms-python.python` | Python | Python 开发支持 |
| `ms-azuretools.vscode-docker` | Docker | 容器管理 |

---

## 3. Step 2: 克隆项目代码

```bash
# 创建项目目录
mkdir -p ~/projects
cd ~/projects

# 克隆项目
git clone https://github.com/your-org/BrainSpark.git
cd BrainSpark

# 查看项目结构
ls -la
```

预期输出应包含：
- `apps/` - 应用目录
- `packages/` - 共享包
- `docs/` - 文档
- `infrastructure/` - 基础设施
- `scripts/` - 脚本
- `package.json` - 根包配置
- `pnpm-workspace.yaml` - 工作区配置
- `turbo.json` - Turborepo 配置

---

## 4. Step 3: 安装项目依赖

```bash
# 进入项目目录
cd BrainSpark

# 安装所有依赖
pnpm install
```

安装过程可能持续几分钟，取决于网络速度。安装完成后，您应该看到类似输出：

```
Packages: +xxx
 +-xxx
...
Done in x.xxxs
```

如果需要单独更新某个应用的依赖：

```bash
# 只更新学生端依赖
pnpm --filter @brainspark/student add <package-name>

# 更新共享类型包
pnpm --filter @brainspark/shared-types add <package-name>
```

---

## 5. Step 4: 启动基础设施服务

### 5.1 检查 Docker 状态

```bash
# 确认 Docker 正在运行
docker info

# 查看已有容器（应该为空）
docker ps
```

### 5.2 创建基础设施配置文件

创建 `infra/docker/` 目录：

```bash
mkdir -p infra/docker
```

创建主配置文件 [`infra/docker/docker-compose.yml`](../../infra/docker/docker-compose.yml:1)：

```yaml
version: '3.8'

x-common-vars: &common-vars
  MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-devpassword}
  MYSQL_DATABASE: ${MYSQL_DATABASE:-brainspark_dev}
  REDIS_PASSWORD: ${REDIS_PASSWORD:-devredis}

services:
  # MySQL
  mysql:
    image: mysql:8.0
    container_name: brainspark-mysql-dev
    command: --default-authentication-plugin=caching_sha2_password
    environment: *common-vars
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql/init.sql:/docker-entrypoint-initdb.d/01-init.sql
    networks:
      - brainspark-dev
    restart: unless-stopped

  # Redis
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

  # MongoDB
  mongodb:
    image: mongo:7
    container_name: brainspark-mongo-dev
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-devpassword}
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    networks:
      - brainspark-dev
    restart: unless-stopped

  # Kafka
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    container_name: brainspark-zookeeper-dev
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    ports:
      - "2181:2181"
    networks:
      - brainspark-dev
    restart: unless-stopped

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: brainspark-kafka-dev
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    ports:
      - "9092:9092"
    depends_on:
      - zookeeper
    networks:
      - brainspark-dev
    restart: unless-stopped

  # ClickHouse
  clickhouse:
    image: clickhouse/clickhouse-server:23.8
    container_name: brainspark-clickhouse-dev
    ports:
      - "8123:8123"
      - "9000:9000"
    volumes:
      - clickhouse_data:/var/lib/clickhouse
    networks:
      - brainspark-dev
    restart: unless-stopped

  # Milvus (包括 etcd 和 minio)
  minio:
    image: minio/minio:latest
    container_name: brainspark-minio-dev
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
    volumes:
      - minio_data:/data
    networks:
      - brainspark-dev
    restart: unless-stopped

  etcd:
    image: quay.io/coreos/etcd:v3.5.12
    container_name: brainspark-etcd-dev
    command: etcd -name etcd0 -listen-client-urls http://0.0.0.0:2379 -advertise-client-urls http://0.0.0.0:2379
    ports:
      - "2379:2379"
    networks:
      - brainspark-dev
    restart: unless-stopped

  milvus:
    image: milvusdb/milvus:v2.4.0
    container_name: brainspark-milvus-dev
    command: ["milvus", "run", "standalone"]
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
    ports:
      - "19530:19530"
    depends_on:
      - etcd
      - minio
    networks:
      - brainspark-dev
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:
  mongo_data:
  clickhouse_data:
  minio_data:

networks:
  brainspark-dev:
    driver: bridge
```

### 5.3 创建必要的配置文件

**MySQL 初始化脚本** [`infra/docker/mysql/init.sql`](../../infra/docker/mysql/init.sql:1):

```sql
CREATE DATABASE IF NOT EXISTS brainspark_dev DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS brainspark_analytics DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**Redis 配置** [`infra/docker/redis/dev.conf`](../../infra/docker/redis/dev.conf:1):

```conf
bind 0.0.0.0
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### 5.4 启动所有基础设施服务

```bash
cd infra/docker

# 启动所有服务
docker compose up -d

# 查看启动状态
docker compose ps

# 查看日志
docker compose logs -f
```

首次启动可能需要几分钟下载镜像。启动完成后，执行 `docker compose ps` 应该显示所有服务状态为 `running`。

### 5.5 验证基础设施服务

```bash
# 测试 MySQL
docker exec -it brainspark-mysql-dev mysql -uroot -pdevpassword -e "SHOW DATABASES;"

# 测试 Redis
docker exec -it brainspark-redis-dev redis-cli -a devredis PING
# 应该返回: PONG

# 测试 MongoDB
docker exec -it brainspark-mongo-dev mongosh --eval "db.runCommand({ ping: 1 })"
```

---

## 6. Step 5: 配置环境变量

### 6.1 前端环境变量

为每个前端应用创建环境变量文件：

**学生端** [`apps/student-web/.env.local`](../../apps/student-web/.env.local:1):

```env
# API 地址
VITE_API_BASE_URL=http://localhost:8082/api/v1

# WebSocket
VITE_WS_URL=ws://localhost:8082

# 应用标题
VITE_APP_TITLE=BrainSpark Student

# 功能开关
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_AI=false
```

**家长端** [`apps/parent-web/.env.local`](../../apps/parent-web/.env.local:1):

```env
VITE_API_BASE_URL=http://localhost:8082/api/v1
VITE_WS_URL=ws://localhost:8082
VITE_APP_TITLE=BrainSpark Parent
```

**教师端** [`apps/teacher-web/.env.local`](../../apps/teacher-web/.env.local:1):

```env
VITE_API_BASE_URL=http://localhost:8082/api/v1
VITE_WS_URL=ws://localhost:8082
VITE_APP_TITLE=BrainSpark Teacher
```

### 6.2 Java 后端环境变量

创建 [`apps/backend-business/src/main/resources/application-dev.yml`](../../apps/backend-business/src/main/resources/application-dev.yml:1):

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/brainspark_dev?useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true
    username: root
    password: devpassword
    driver-class-name: com.mysql.cj.jdbc.Driver
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        format_sql: true
  redis:
    host: localhost
    port: 6379
    password: devredis
    timeout: 5000ms

server:
  port: 8081

logging:
  level:
    com.brainspark: DEBUG
    org.hibernate.SQL: DEBUG
```

### 6.3 Go 网关环境变量

创建 [`apps/backend-gateway/.env`](../../apps/backend-gateway/.env:1):

```env
GIN_MODE=debug
PORT=8082
BACKEND_BUSINESS_URL=http://localhost:8081
LOG_LEVEL=debug
ACCESS_LOG_ENABLED=true
```

### 6.4 Python AI 服务环境变量

创建 [`apps/ai-service/.env`](../../apps/ai-service/.env:1):

```env
AI_PROVIDER=qwen
API_KEY=your_test_api_key_here
VECTOR_STORE=milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
LOG_LEVEL=DEBUG
```

---

## 7. Step 6: 初始化数据库

```bash
# 进入 docker 目录
cd infra/docker

# 验证 MySQL 连接
docker exec -it brainspark-mysql-dev mysql -uroot -pdevpassword brainspark_dev -e "SELECT 1;"

# 执行初始化 SQL（如果有更复杂的初始化脚本）
docker exec -i brainspark-mysql-dev mysql -uroot -pdevpassword < ./mysql/init.sql
```

预期输出应确认连接成功且数据库已创建。

---

## 8. Step 7: 启动开发服务

### 8.1 启动所有服务（Turbo 模式）

在项目根目录执行：

```bash
# 从 infra/docker 返回项目根目录
cd ../..

# 启动所有开发服务
pnpm dev:all
```

### 8.2 分别启动各服务

#### 前端服务

```bash
# 学生端
pnpm dev:student
# 启动后访问: http://localhost:5173

# 家长端
pnpm dev:parent
# 启动后访问: http://localhost:5174

# 教师端
pnpm dev:teacher
# 启动后访问: http://localhost:5175
```

#### Java 后端

```bash
cd apps/backend-business

# 启动 Spring Boot
mvn spring-boot:run
# 启动后访问: http://localhost:8081
```

#### Go 网关

```bash
cd apps/backend-gateway

# 启动网关
go run main.go
# 启动后网关代理: http://localhost:8082
```

#### Python AI 服务

```bash
cd apps/ai-service

# 创建虚拟环境（首次）
python -m venv venv
# Windows 激活:
venv\Scripts\activate
# macOS/Linux 激活:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动 API 服务
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
# 启动后访问: http://localhost:8000/docs
```

---

## 9. Step 8: 验证安装

### 9.1 快速验证脚本

创建 [`scripts/verify-environment.sh`](../../scripts/verify-environment.sh:1)：

```bash
#!/bin/bash
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "===================================="
echo "  BrainSpark 开发环境验证"
echo "===================================="
echo ""

# 检查工具
check_command() {
  if command -v $1 &> /dev/null; then
    echo -e "${GREEN}✓${NC} $(echo "$2" | awk '{print $1}': $(command -v $1))"
  else
    echo -e "${RED}✗${NC} 未找到: $(echo "$1" | awk '{print $1}')"
  fi
}

check_command node "Node.js"
check_command pnpm "pnpm"
check_command docker "Docker"
check_command java "Java"
check_command mvn "Maven"
check_command go "Go"
check_command python3 "Python"

echo ""

# 检查 Docker 容器
echo "--- 基础设施服务状态 ---"
cd infra/docker
STATUS=$(docker compose ps --format table --filter "status=running")
if [ -n "$STATUS" ]; then
  echo -e "${GREEN}✓${NC} 运行中的容器:  $(echo "$STATUS" | grep -c "Up" || true) / $(echo "$STATUS" | wc -l | tr -d ' ')"
else
  echo -e "${RED}✗${NC} 没有运行中的基础设施容器"
fi

cd ../..

echo ""
echo "===================================="
echo "  验证完成!"
echo "===================================="
```

在 Linux/macOS 上：
```bash
chmod +x scripts/verify-environment.sh
./scripts/verify-environment.sh
```

在 Windows (PowerShell) 上：
```powershell
.\scripts\verify-environment.ps1
```

### 9.2 服务可用性测试

```bash
# 测试 API 网关
curl http://localhost:8082/api/v1/health

# 测试业务后端
curl http://localhost:8081/actuator/health

# 测试 AI 服务文档
curl http://localhost:8000/docs

# 测试 MySQL
docker exec brainspark-mysql-dev mysql -uroot -pdevpassword -e "SELECT VERSION();"

# 测试 Redis
docker exec brainspark-redis-dev redis-cli -a devredis ping

# 检查前端端口
ss -tlnp | grep -E '517[3-5]'
```

### 9.3 功能验证清单

| 服务 | URL | 验证方式 |
|------|-----|---------|
| 学生端前端 | http://localhost:5173 | 页面正常加载 |
| 家长端前端 | http://localhost:5174 | 页面正常加载 |
| 教师端前端 | http://localhost:5175 | 页面正常加载 |
| API 网关 | http://localhost:8082 | 可访问 |
| 业务后端 | http://localhost:8081 | Actuator 健康检查通过 |
| AI 服务 | http://localhost:8000/docs | Swagger UI 可访问 |
| MySQL | localhost:3306 | 客户端连接成功 |
| Redis | localhost:6379 | `PING` 返回 `PONG` |
| MongoDB | localhost:27017 | 客户端连接成功 |
| Kafka | localhost:9092 | Broker 可连接 |
| Milvus | localhost:19530 | 向量搜索可用 |

---

## 10. 常见问题排查

### 10.1 端口冲突

**症状：** 服务启动时提示 address already in use

**解决方案：**
```bash
# Windows 查找占用端口的进程
netstat -ano | findstr :3306

# 查找并终止进程
taskkill /PID <PID> /F

# 或修改 docker-compose.yml 中的端口映射
# "3306:3306" 改为 "3307:3306"
```

### 10.2 Docker 容器无法启动

**症状：** `docker compose up` 启动失败

**排查步骤：**
```bash
# 查看详细日志
docker compose logs mysql

# 重启容器
docker compose restart

# 重新拉取镜像
docker compose pull

# 完全重建
docker compose down -v
docker compose up --build -d
```

### 10.3 Java 后端连接失败

**症状：** Spring Boot 启动后无法连接 MySQL

**排查：**
```bash
# 检查 MySQL 是否运行
docker ps | grep mysql

# 测试连接
docker exec -it brainspark-mysql-dev mysql -uroot -pdevpassword -e "SELECT 1;"

# 确认 application-dev.yml 配置正确
cat apps/backend-business/src/main/resources/application-dev.yml

# 确认激活的 profile
mvn spring-boot:run -Dspring-boot.run.profiles=dev
```

### 10.4 Go 网关连接失败

**症状：** 网关启动后无法代理请求

**排查：**
```bash
# 检查后端服务是否启动
curl http://localhost:8081/actuator/health

# 检查 Go 环境变量
cat apps/backend-gateway/.env

# 使用 verbose 模式启动
go run main.go 2>&1 | head -n 50
```

### 10.5 pnpm 依赖安装失败

**症状：** `pnpm install` 报超时或下载错误

**解决方案：**
```bash
# 清除 pnpm 缓存
pnpm cache clean

# 删除依赖重新安装
rm -rf node_modules
rm pnpm-lock.yaml
pnpm install

# 使用淘宝镜像（中国大陆用户）
pnpm config set registry https://registry.npmmirror.com
```

### 10.6 前端无法连接后端

**症状：** 前端发起 API 请求失败，Network 面板显示错误

**排查：**
```bash
# 确认 .env.local 文件已创建
cat apps/student-web/.env.local

# 确认网关正常运行
curl http://localhost:8082/actuator/health

# 检查 CORS 配置（如有问题）
# 确认后端和网关的 CORS 允许 localhost
```

---

## 11. 附录

### 11.1 服务端口速查表

| 服务 | 端口 | 协议 | 用途 |
|------|------|------|------|
| student-web | 5173 | HTTP | 学生端前端开发服务器 |
| parent-web | 5174 | HTTP | 家长端前端开发服务器 |
| teacher-web | 5175 | HTTP | 教师端前端开发服务器 |
| backend-business | 8081 | HTTP | Java 业务后端 |
| backend-gateway | 8082 | HTTP | Go API 网关 |
| ai-service | 8000 | HTTP | Python AI 服务 |
| MySQL | 3306 | TCP | 业务数据库 |
| Redis | 6379 | TCP | 缓存和会话存储 |
| MongoDB | 27017 | TCP | 行为数据存储 |
| Kafka | 9092 | TCP | 消息队列 |
| ClickHouse | 8123, 9000 | HTTP/TCP | 分析数据存储 |
| Milvus | 19530 | TCP | 向量数据库 |
| MinIO | 9000, 9001 | HTTP | 对象存储 |
| etcd | 2379 | HTTP | KV 存储 |
| Zookeeper | 2181 | TCP | Kafka 协调 |

### 11.2 常用管理命令

```bash
# ============ 项目级 ============

# 安装所有依赖
pnpm install

# 启动所有开发服务
pnpm dev:all

# 启动单个服务
pnpm dev:student      # 学生端
pnpm dev:parent       # 家长端
pnpm dev:teacher      # 教师端

# 构建
pnpm build:all

# 代码检查
pnpm lint:all
pnpm typecheck:all

# ============ Docker 级 ============

cd infra/docker

# 启动
docker compose up -d

# 停止
docker compose down

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f

# 单独启动/停止服务
docker compose up -d mysql redis
docker compose stop kafka

# ============ Git ============

# 查看状态
git status

# 提交
git add .
git commit -m "feat(student-web): implement feature"

# 创建功能分支
git checkout -b feat/my-feature

# 查看分支
git branch -a
```

### 11.3 VS Code 调试配置

创建 [`.vscode/launch.json`](../../.vscode/launch.json:1)（如果不存在）：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Student Web",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/apps/student-web/src",
      "sourceMapIgnoreList": ["/**/node_modules/**"]
    },
    {
      "name": "Debug Java Backend",
      "type": "java",
      "request": "launch",
      "mainClass": "com.brainspark.BrainSparkApplication",
      "projectName": "backend-business",
      "args": "--spring.profiles.active=dev",
      "console": "integratedTerminal"
    },
    {
      "name": "Debug Go Gateway",
      "type": "go",
      "request": "launch",
      "mode": "debug",
      "program": "${workspaceFolder}/apps/backend-gateway"
    },
    {
      "name": "Debug AI Service (Uvicorn)",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--port", "8000"],
      "cwd": "${workspaceFolder}/apps/ai-service",
      "env": {
        "AI_PROVIDER": "qwen",
        "LOG_LEVEL": "DEBUG"
      }
    }
  ]
}
```

### 11.4 健康检查 API

| 服务 | 端点 | 预期响应 |
|------|------|---------|
| Spring Boot | `GET http://localhost:8081/actuator/health` | `{"status":"UP"}` |
| AI 服务 | `GET http://localhost:8000/health` | `{"status":"ok"}` |
| API 网关 | `GET http://localhost:8082/health` | `{"status":"ok"}` |

---

> 本文档为安装配置手册，创建于 2026-05-20。