# BrainSpark 系统架构设计

> 版本: 1.0.0 | 最后更新: 2026-05-19

## 目录

1. [设计文档索引](#设计文档索引)
2. [系统概览](#系统概览)
3. [架构分层](#架构分层)
4. [数据架构](#数据架构)
5. [消息队列](#消息队列)
6. [配置管理](#配置管理)
7. [部署架构](#部署架构)

## 设计文档索引

本文档是 BrainSpark 平台架构设计的总览。各个核心模块的详细设计已拆分为独立文档，请参阅：

| # | 模块 | 详细设计文档 | 核心内容 |
|---|------|-------------|----------|
| 1 | 学生端 (`student-web`) | [`student-web-design.md`](./student-web-design.md) | PixiJS WebGL 游戏引擎、`performance.now()` 微秒级采集、IndexedDB 断点续测 |
| 2 | 教师端 (`teacher-web`) | [`teacher-web-design.md`](./teacher-web-design.md) | 班级/学生管理、测评布置、报告批注、数据看板 |
| 3 | 家长端 (`parent-web`) | [`parent-web-design.md`](./parent-web-design.md) (参考 [`scheme.md`](./scheme.md)) | 成长趋势可视化、订阅管理、报告下载 |
| 4 | 接入与网关层 | [`gateway-design.md`](./gateway-design.md) | Nginx 反代与 SSL 终结、Go 高并发网关、限流/RequestId/WebSocket |
| 5 | 后端业务服务 | [`business-backend-design.md`](./business-backend-design.md) | Java Spring Boot 3、用户/测评/订单/管理员 API、MySQL 核心 Schema |
| 6 | AI 服务 | [`ai-service-design.md`](./ai-service-design.md) | FastAPI + LangChain、认知分析引擎、报告生成 Prompt |
| 7 | 业务中台 | [`middleware-design.md`](./middleware-design.md) | 用户与合规 (监护人同意)、测评引擎 (状态机/反作弊)、报告与档案、内容商城 (订阅) |
| 8 | AI 与数据引擎 | [`data-engine-design.md`](./data-engine-design.md) | Kafka 消息流、Flink 实时清洗/反作弊、ClickHouse 常模对比、Milvus RAG |
| 9 | 基础设施 | [`infrastructure-design.md`](./infrastructure-design.md) | MySQL 集群、MongoDB/Redis/Kafka 部署、Docker Compose、K8s + Helm、CI/CD |

---

## 系统概览

BrainSpark 采用微服务架构，通过 Kubernetes 进行容器编排管理。各服务通过 API Gateway 统一暴露，内部服务间通过 REST/GRPC 进行通信。

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                            Client Layer                                        │
│   Student App      Parent App       Teacher App    Operator Web       CLI/Scripts  │
└─────────┬───────────┬───────────────┬──────────────┬────────────────────────────┘
          │           │               │              │
┌─────────▼───────────▼───────────────▼──────────────▼────────────────────────────┐
│                            Nginx Layer                                            │
│                    Reverse Proxy + SSL Termination                                │
│   │         │          │          │         │              │         │            │
│  student  parent     teacher  operator  backend   │  ai-service   static          │
│   :3000    :3001      :3002     :3003      :8080  │   :8001           │           │
└─────────┬───────────┬───────────┬────────┬──────┬──────────────────────────┘
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
| operator-web | Vue3 + Element Plus | 3003 | 运营管理后台 + 运维监控面板 |

### 1.1 运营管理应用 (Operator Web)

| 模块 | 功能说明 | 角色 |
|------|----------|------|
| 数据统计看板 | 注册/付费转化/活跃统计 | OPERATOR, ADMIN |
| 内容管理 | 商品/套餐配置 | OPERATOR, ADMIN |
| 知识库管理 | RAG教育知识内容维护 | OPERATOR |
| 机构合作 | 审批/合同/结算 | OPERATOR, ADMIN |
| 通知管理 | 群发通知/推送 | OPERATOR |
| 系统配置 | 平台参数/权限配置 | ADMIN |

### 1.2 运维监控面板 (Operator Web - 子模块)

| 模块 | 功能说明 | 访问方式 |
|------|----------|----------|
| 服务健康监控 | 各服务UP/DOWN状态 | IP白名单 |
| 性能仪表盘 | QPS、响应时间、错误率 | IP白名单 |
| 日志查询 | 关键字检索、分级过滤 | IP白名单 |
| 实例管理 | 容器/Pod状态查看 | IP白名单 |

### 2. 网关层 (Gateway Layer)

#### Nginx
```
- SSL Termination
- Static file server
- Request routing by path:
  /student/*     -> student-app:3000
  /parent/*      -> parent-app:3001
  /teacher/*     -> teacher-app:3002
  /operator/*    -> operator-web:3003
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
- 用户/班级管理/测评任务/报告 CRUD
- 订单与支付管理（订单状态机、支付网关对接、订阅生命周期）
- 运营管理API（内容/知识库/统计/机构/通知）
- 消息队列异步写入 ClickHouse
- HTTP 接口为 AI Service 提供数据

#### Go 网关服务 (`backend-gateway`)
- 高并发游戏结果上报
- API Gateway (路由分发、限流熔断)
- Request ID 追踪
- WebSocket 连接

#### AI 服务 (`ai-service`)
- FastAPI + LangChain + PyMilvus
- 认知能力向量分析
- LLM报告生成
- 教育知识库检索(RAG)

#### 订单支付服务 (`order-service`)
> **注**: 一期可与 `business-backend` 合并，二期拆分独立服务
- 订单状态机管理 (CREATED -> PENDING_PAY -> PAID -> COMPLETED/REFUNDED)
- 微信支付/支付宝集成
- 订阅生命周期管理（续费、到期提醒、取消与重新激活）
- 发票申请与生成

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
| operator-web | 3003 |
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
│   ├── operator/       # 运营管理后台
│   ├── business/
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
- 运营管理: 256Mi Memory, 0.5 CPU

**资源限制**:
- Java 服务: 2 CPU, 2Gi Memory
- Go 网关: 1 CPU, 1Gi Memory
- AI 服务: 4 CPU, 8Gi Memory (含GPU)
- 前端应用: 256Mi Memory, 0.5 CPU