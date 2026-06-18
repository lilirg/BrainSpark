# BrainSpark 本地数据库服务配置方案

> 版本: 1.1 | 最后更新: 2026-06-07

## 1. 概述

根据项目架构文档，BrainSpark 采用多数据库协同架构。本文档规划了在本地开发环境中通过 Docker Compose 配置全部 5 种数据库服务的完整方案。

> ⚠️ **前置条件**: 本方案依赖 Docker Desktop。如果尚未安装，请先参考 [附录 A](#附录-a-docker-desktop-安装指南) 完成安装。

## 2. 数据库服务清单

| 服务 | 镜像版本 | 端口映射 | 用途 |
|------|---------|---------|------|
| MySQL | mysql:8.0 | 3306:3306 | 核心业务数据 |
| Redis | redis:7-alpine | 6379:6379 | 缓存/锁/限流 |
| MongoDB | mongo:7 | 27017:27017 | 行为事件日志 |
| ClickHouse | clickhouse/clickhouse-server:23.8 | 8123:8123, 9000:9000 | OLAP 分析 |
| Milvus | milvusdb/milvus:v2.4.0 | 19530:19530, 9091:9091 | 向量检索 |
| etcd | quay.io/coreos/etcd:v3.5.12 | 2379:2379 | Milvus 元数据存储 |
| MinIO | minio/minio:latest | 9000:9000, 9001:9001 | Milvus 向量数据存储 |

## 3. 目录结构

```
infra/docker/
├── .env                          # 环境变量（密码等敏感信息）
├── docker-compose.yml            # 主配置文件
├── docker-compose.dev.yml        # 开发环境扩展配置
├── docker-compose.services.yml   # 基础设施服务配置
├── mysql/
│   ├── init.sql                  # 数据库初始化脚本
│   └── conf.d/
│       └── dev.cnf               # 开发环境 MySQL 配置
├── redis/
│   └── dev.conf                  # 开发环境 Redis 配置
├── clickhouse/
│   └── init.sql                  # ClickHouse 初始化脚本
└── nginx/
    └── dev.conf                  # 开发环境反向代理配置
```

## 4. 配置文件详情

### 4.1 `.env` - 环境变量

```env
# MySQL
MYSQL_ROOT_PASSWORD=brainspark_dev
MYSQL_DATABASE=brainspark

# Redis
REDIS_PASSWORD=brainspark_redis

# MongoDB
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=brainspark_dev
MONGO_INITDB_DATABASE=brainspark_behavior

# MinIO (Milvus 依赖)
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
```

### 4.2 `docker-compose.yml` - 主配置

包含全部 7 个服务（MySQL、Redis、MongoDB、ClickHouse、Milvus、etcd、MinIO），配置数据卷持久化、网络隔离、健康检查。

### 4.3 `mysql/init.sql` - MySQL 初始化

创建 4 个业务数据库：
- `users_schema` - 用户与合规数据
- `assessment_schema` - 测评业务数据
- `mall_schema` - 商城与订单数据
- `ai_schema` - AI 服务数据

### 4.4 `mysql/conf.d/dev.cnf` - MySQL 开发配置

- 字符集: utf8mb4
- 排序规则: utf8mb4_unicode_ci
- 开发环境性能调优（降低内存占用）

### 4.5 `redis/dev.conf` - Redis 开发配置

- 绑定 0.0.0.0
- 关闭持久化（开发环境）
- 最大内存 256MB

### 4.6 `clickhouse/init.sql` - ClickHouse 初始化

创建分析型数据库和表：
- `brainspark_analytics` 数据库
- `assessment_event_records` 表
- `assessment_results_agg` 表
- `cognitive_normalize` 表

## 5. 实施步骤

### 步骤 1: 创建目录结构
```bash
mkdir -p infra/docker/mysql/conf.d
mkdir -p infra/docker/redis
mkdir -p infra/docker/clickhouse
mkdir -p infra/docker/nginx
```

### 步骤 2: 创建环境变量文件
创建 `infra/docker/.env` 包含所有数据库密码配置。

### 步骤 3: 创建 MySQL 配置
- `infra/docker/mysql/init.sql` - 初始化脚本
- `infra/docker/mysql/conf.d/dev.cnf` - 开发配置

### 步骤 4: 创建 Redis 配置
- `infra/docker/redis/dev.conf` - 开发配置

### 步骤 5: 创建 ClickHouse 配置
- `infra/docker/clickhouse/init.sql` - 初始化脚本

### 步骤 6: 创建 Docker Compose 主配置
- `infra/docker/docker-compose.yml` - 主编排文件

### 步骤 7: 创建 Nginx 配置
- `infra/docker/nginx/dev.conf` - 反向代理配置

### 步骤 8: 启动服务
```bash
cd infra/docker
docker compose up -d
```

### 步骤 9: 验证服务
```bash
# 检查所有容器状态
docker compose ps

# 验证 MySQL 连接
docker compose exec mysql mysql -uroot -pbrainspark_dev -e "SHOW DATABASES;"

# 验证 Redis 连接
docker compose exec redis redis-cli -a brainspark_redis PING

# 验证 MongoDB 连接
docker compose exec mongodb mongosh -u root -p brainspark_dev --eval "db.runCommand({ping:1})"

# 验证 ClickHouse 连接
docker compose exec clickhouse clickhouse-client --query "SELECT 1"
```

## 6. 各服务连接信息

| 服务 | 连接地址 | 用户名 | 密码 |
|------|---------|--------|------|
| MySQL | localhost:3306 | root | brainspark_dev |
| Redis | localhost:6379 | - | brainspark_redis |
| MongoDB | localhost:27017 | root | brainspark_dev |
| ClickHouse | localhost:8123 (HTTP) / localhost:9000 (Native) | default | (空) |
| Milvus | localhost:19530 | - | - |

## 7. 各应用配置更新

### Python 后端 (`apps/backend-python/.env`)
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=brainspark_dev
DB_NAME=brainspark

MONGO_URI=mongodb://root:brainspark_dev@localhost:27017
MONGO_DB=brainspark_behavior

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=brainspark_redis

CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_DB=brainspark_analytics
```

### Java 后端 (`apps/backend-business/src/main/resources/application.yml`)
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/brainspark?useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true
    username: root
    password: brainspark_dev
  data:
    mongodb:
      uri: mongodb://root:brainspark_dev@localhost:27017/brainspark_behavior
```

## 8. 常用命令

```bash
# 启动所有服务
cd infra/docker && docker compose up -d

# 启动指定服务
docker compose up -d mysql redis

# 查看日志
docker compose logs -f mysql

# 停止所有服务
docker compose down

# 停止并删除数据卷（危险！会丢失所有数据）
docker compose down -v

# 重启服务
docker compose restart mysql
```

## 9. 注意事项

1. **Docker Desktop 要求**: 确保已安装 Docker Desktop for Windows，并启用 WSL 2 后端
2. **资源占用**: 全部 7 个容器约占用 4-6 GB 内存，建议开发机至少 16 GB 内存
3. **端口冲突**: 确保本地 3306、6379、27017、8123、9000、19530、2379、9091、9092 端口未被占用
4. **数据持久化**: 数据卷存储在 Docker 管理目录中，`docker compose down -v` 会删除所有数据
5. **首次启动**: Milvus 首次启动需要拉取 etcd 和 MinIO 镜像，耗时较长
6. **生产环境**: 此配置仅用于开发环境，生产环境需使用强密码和 SSL/TLS 加密

---

## 附录 A: Docker Desktop 安装指南

### Windows 11 安装步骤

1. **启用 WSL 2**
   ```powershell
   # 以管理员身份运行 PowerShell
   wsl --install
   # 安装完成后重启电脑
   ```

2. **下载 Docker Desktop**
   - 访问 https://www.docker.com/products/docker-desktop/
   - 下载 Windows 版本安装包

3. **安装 Docker Desktop**
   - 双击安装包，按向导完成安装
   - 安装时勾选 "Use WSL 2 instead of Hyper-V"
   - 安装完成后重启电脑

4. **启动 Docker Desktop**
   - 从开始菜单启动 Docker Desktop
   - 等待状态栏显示 "Engine running"
   - 在 Settings → Resources → WSL Integration 中，确保启用与 WSL 的集成

5. **验证安装**
   ```powershell
   # 打开新的 PowerShell 或 CMD 窗口
   docker --version
   docker compose version
   ```

6. **配置镜像加速（可选，国内用户推荐）**
   - 打开 Docker Desktop → Settings → Docker Engine
   - 添加 registry-mirrors 配置：
   ```json
   {
     "registry-mirrors": [
       "https://docker.mirrors.ustc.edu.cn",
       "https://hub-mirror.c.163.com"
     ]
   }
   ```
   - 点击 "Apply & Restart"

### 安装后验证

```powershell
# 确认 Docker 可用
docker run hello-world

# 确认 Docker Compose 可用
docker compose version
```