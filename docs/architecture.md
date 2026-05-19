# BrainSpark 系统架构设计

> 版本: 1.0.0 | 最后更新: 2026-05-19

## 目录

1. [系统概览](#系统概览)
2. [架构分层](#架构分层)
3. [服务设计](#服务设计)
4. [数据架构](#数据架构)
5. [API 设计](#api-设计)
6. [基础设施](#基础设施)
7. [部署架构](#部署架构)

## 系统概览

BrainSpark 采用微服务架构，通过 Kubernetes 进行容器编排管理。各服务通过 API Gateway 统一暴露，内部服务间通过 REST/GRPC 进行通信。

```
┌─────────────────────────────────────────────────────────────────────┐
│                            Client Layer                              │
│   Student App      Parent App       Teacher App       CLI/Scripts   │
└─────────┬───────────┬───────────────┬──────────────────────────────┘
          │           │               │
┌─────────▼───────────▼───────────────▼──────────────────────────────┐
│                            Nginx Layer                               │
│                    Reverse Proxy + SSL Termination                   │
│   │         │          │          │          │          │           │
│  student  parent     teacher  backend  │  ai-service   static        │
│   :3000    :3001      :3002      :8080  │   :8001           │        │
└─────────┬───────────┬───────────┬──────┬──────────────────────────┘
          │           │           │      │
┌─────────▼───────────▼───────────▼──────▼──────────────────────────┐
│                         Backend Cluster                             │
│                                                                      │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────┐ │
│  │ business-backend │    │  backend-gateway │    │ ai-service   │ │
│  │   Spring Boot    │    │      Go Gin      │    │ FastAPI      │ │
│  │    :8080         │    │     :8081        │    │   :8001      │ │
│  └────────┬─────────┘    └────────┬─────────┘    └──────┬───────┘ │
│           │                       │                     │         │
│  ┌────────▼───────────────────────▼─────────────────────▼───────┐ │
│  │                         Message Bus                           │ │
│  │                      Redis + Kafka                            │ │
│  └───────────────┬─────────────────────┬──────────────────────┘ │
│                  │                     │                         │
│  ┌───────────────▼──────┐  ┌──────────▼──────────┐             │
│  │   MySQL 8.0          │  │   MongoDB             │             │
│  │   Users/Cases/Tasks  │  │   Behavior/Logs       │             │
│  └──────────────────────┘  └─────────────────────┘             │
│                                                                  │
│  ┌──────────────────────┐  ┌───────────────────┐                │
│  │   ClickHouse         │  │   Milvus            │                │
│  │   Analytics          │  │   Vector DB         │                │
│  └──────────────────────┘  └───────────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
```

## 架构分层

### 1. 客户端层 (Client Layer)

| 应用 | 技术栈 | 端口 | 说明 |
|------|--------|------|------|
| student-app | Vue3 + PixiJS | 3000 | WebGL游戏测评 |
| parent-app | Vue3 + Element Plus | 3001 | 家长仪表板 |
| teacher-app | Vue3 + Element Plus | 3002 | 教师管理后台 |

### 2. 网关层 (Gateway Layer)

#### Nginx
```
- SSL Termination
- Static file server
- Request routing by path:
  /student/*     -> student-app:3000
  /parent/*      -> parent-app:3001
  /teacher/*     -> teacher-app:3002
  /api/*         -> backend-gateway:8081
  /ai/*          -> ai-service:8001
```

#### Go 网关 (`backend-gateway`)
- 高并发游戏结果收集
- Rate Limiting (基于IP)
- Request ID 追踪
- WebSocket 连接

### 3. 服务层 (Service Layer)

#### Java 业务服务 (`business-backend`)
- 用户认证 (JWT)
- 用户/C端/任务/报告 CRUD
- 消息队列异步写入 ClickHouse
- HTTP 接口为 AI Service 提供数据

#### AI 服务 (`ai-service`)
- FastAPI + LangChain + PyMilvus
- 认知能力向量分析
- LLM报告生成
- 教育知识库检索(RAG)

### 4. 数据层 (Data Layer)

| 数据库 | 用途 |
|--------|------|
| MySQL | 用户/权限/班级管理/测评任务 |
| MongoDB | 用户行为轨迹/非结构化数据 |
| ClickHouse | 测评分析/常模对比 |
| Milvus | 教育知识库向量存储 |
| Redis | 缓存/Session/限流 |

## 数据流图

### 测评流程

```
student-app ───POST /api/v1/assessment/submit───▶ Gateway ──异步──▶ ClickHouse
     │                                                    │
     │                              business-backend      │
     │ ────────────────POST /api/v1/assessment/today─────▶│
     │                                                    │
     │                              ai-service            │
     │                              ──────分析─────▶      │
     │ ◀─────────200/分析结果──────────────────────────────│
```

### AI报告生成

```
teacher-app ◀───GET /api/v1/report/{id}──────────── Teacher
     │
     │
     │ POST /ai/v1/analysis/
     │ {assessment_results: [...]}
     │
     │
▼ ai-service (FastAPI)
     │
     ├──▶ analyze cognitive dimensions (Python统计)
     │
     └──▶ RAG 检索:
          │
          └──▶ Milvus (教育知识库向量搜索)
               │
               └──▶ GPT-4o/本地大模型
                    │
                    └──▶ 生成结构化报告 (HTML/PDF)
```

## 消息队列

```
                Kafka (可选，二期实施)
                    │
    ┌───────────────┼───────────────┐
    │               │               │
 Gateway   business-backend    analytics-service
  (发布      (消费并发布       (消费 ClickHouse
  消息)       消息)             插入/聚合)
```

**一期实施策略**：
1. Gateway 直接插入 ClickHouse
2. business-backend 异步线程推送

## 配置管理

### 环境变量映射

```yaml
# .env (Gateway)
GATEWAY_PORT=8081
CLICKHOUSE_URL=ch://clickhouse:9000
CLICKHOUSE_DATABASE=brainspark

# .env (business-backend)
SPRING_DATASOURCE_URL=jdbc:mysql://mysql:3306/brainspark
SPRING_DATA_MONGODB_URI=mongodb://mongo:27017/brainspark

# .env (ai-service)
OPENAI_API_KEY=your_key
MILVUS_URI=http://milvus:19530
REDIS_URL=redis://redis:6379
```

## 部署架构

### 开发环境 (Docker Compose)

```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d
```

| 服务 | 端口 |
|------|------|
| student-app | 3000 |
| parent-app | 3001 |
| teacher-app | 3002 |
| business-backend | 8080 |
| backend-gateway | 8081 |
| ai-service | 8001 |
| mysql | 3306 |
| mongo | 27017 |
| clickhouse | 8123/9000 |
| milvus | 19530 |
| redis | 6379 |
| nginx | 80/443 |

### 生产环境 (Kubernetes)

```yaml
infra/k8s/
├── base/
│   ├── namespace.yaml
│   └── common-deploy.yaml
├── apps/
│   ├── student/
│   ├── parent/
│   ├── teacher/
│   ├── backend/
│   ├── gateway/
│   └── ai/
└── ingress/
    └── routes.yaml
```

**资源限制**:
- Java 服务: 2 CPU, 2Gi Memory
- Go 网关: 1 CPU, 1Gi Memory
- AI 服务: 4 CPU, 8Gi Memory (含GPU)
- 前端应用: 256Mi Memory, 0.5 CPU