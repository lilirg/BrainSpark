# BrainSpark 仓库结构设计

## 🏗️ 整体架构

```
BrainSpark/                          # 根目录 (Monorepo)
├── packages/                        # 共享包
│   ├── types/                       # TypeScript 类型定义
│   ├── shared-utils/                # 公共工具函数
│   └── ui-components/               # 可复用UI组件库
├── apps/                            # 应用模块
│   ├── student-app/                 # 学生端 (Vue3 + PixiJS)
│   ├── parent-app/                  # 家长端 (Vue3 + Element Plus/Vant)
│   ├── teacher-app/                 # 教师端 (Vue3 + Element Plus)
│   ├── business-backend/            # Java 业务后端 (Spring Boot 3)
│   ├── gateway-backend/             # Go 高并发网关 (Gin)
│   ├── ai-service/                  # AI 推理服务 (FastAPI)
│   └── analytics-engine/            # ClickHouse OLAP 分析服务 (Go/Python)
├── infra/                           # 基础设施配置
│   ├── docker/                      # Docker Compose 配置
│   ├── k8s/                         # Kubernetes 部署
│   ├── nginx/                       # Nginx 配置
│   └── scripts/                     # 运维脚本
├── tools/                           # 开发工具
│   ├── code-gen/                    # 代码生成器
│   └── test-utils/                  # 测试工具库
├── docs/                            # 项目文档
├── scripts/                         # 构建和CI脚本
├── pnpm-workspace.yaml              # PNPM workspace 配置
├── package.json                     # 根 package.json
├── turbo.json                       # Turborepo 构建配置
├── Dockerfile                       # 容器化配置
└── docker-compose.yml               # 本地开发环境
```

## 📦 模块详情

### 1. 前端应用

#### `apps/student-app/` - 学生端 (测评游戏引擎)
- **技术栈**: Vue3 + Vite + TypeScript + PixiJS (WebGL)
- **端口**: 3000
- **核心模块**:
  ```
  student-app/
  ├── src/
  │   ├── components/           # 基础UI组件
  │   ├── games/               # 测评游戏逻辑
  │   │   ├── memory/         # 记忆力游戏
  │   │   ├── attention/      # 注意力游戏
  │   │   ├── logic/          # 逻辑力游戏
  │   │   └── imagination/    # 想象力游戏
  │   ├── engines/             # PixiJS 渲染引擎
  │   ├── views/              # 页面视图
  │   └── stores/             # Pinia 状态管理
  ├── package.json
  └── vite.config.ts
  ```

#### `apps/parent-app/` - 家长端
- **技术栈**: Vue3 + Vite + TypeScript + Element Plus/Vant (移动端)
- **端口**: 3001

#### `apps/teacher-app/` - 教师端
- **技术栈**: Vue3 + Vite + TypeScript + Element Plus
- **端口**: 3002

### 2. 后端服务

#### `apps/business-backend/` - Java 业务后端 (8080)
- **技术栈**: Spring Boot 3 + Java 17 + MyBatis-Plus
- **职责**: 用户管理、班级管理、测评任务、报告管理等核心业务
- **核心包结构**:
  ```
  business-backend/
  ├── src/main/java/com/brainspark/
  │   ├── controller/         # REST API 控制器
  │   ├── service/           # 业务逻辑
  │   ├── mapper/            # MyBatis-Plus Mapper
  │   ├── entity/            # JPA 实体
  │   ├── dto/               # 数据传输对象
  │   ├── config/            # 配置类
  │   └── security/          # 安全配置
  ├── src/main/resources/
  │   ├── application.yml    # 应用配置
  │   └── mapper/            # XML 映射
  ├── pom.xml
  └── Dockerfile
  ```

#### `apps/gateway-backend/` - Go 高并发网关 (8081)
- **技术栈**: Go 1.21 + Gin + Redis + ClickHouse Go
- **职责**: 测评游戏结果上报、API网关、限流熔断、实时监控
- **核心包结构**:
  ```
  gateway-backend/
  ├── cmd/server/            # 入口
  ├── internal/
  │   ├── handler/          # HTTP处理器
  │   ├── middleware/       # 中间件(限流/日志/认证)
  │   ├── writer/           # ClickHouse写入
  │   └── model/           # 数据模型
  ├── config/               # 配置文件
  ├── Makefile
  └── Dockerfile
  ```

#### `apps/ai-service/` - AI 推理服务 (8001)
- **技术栈**: Python + FastAPI + LangChain + OpenAI API
- **职责**: 能力评估分析、RAG知识检索、智能报告生成、训练计划制定
- **核心模块结构**:
  ```
  ai-service/
  ├── app/
  │   ├── main.py           # FastAPI 入口
  │   ├── api/              # API路由
  │   ├── core/             # 核心配置
  │   ├── models/           # ML模型加载
  │   ├── services/         # 业务服务(LLM/向量DB)
  │   └── schemas/          # Pydantic 模型
  ├── tests/
  ├── requirements.txt
  ├── Dockerfile
  └── .env.example
  ```

### 3. 共享包

#### `packages/types/` - 全局类型定义
```typescript
// types/src/user.ts - 用户类型
export interface User {
  id: string;
  username: string;
  role: 'admin' | 'teacher' | 'student' | 'parent';
  profile?: UserProfile;
}

// types/src/assessment.ts - 测评相关类型
export interface AssessmentTask {
  id: string;
  name: string;
  type: AssessmentType;
  games: GameConfig[];
}

export interface AssessmentResult {
  id: string;
  studentId: string;
  taskId: string;
  dimensions: CognitiveDimensions;
  createdAt: string;
}

// 认知维度评分
export interface CognitiveDimensions {
  memory: number;      // 记忆力
  attention: number;   // 注意力
  logic: number;       // 逻辑力
  creativity: number;  // 创造力
  observation: number; // 观察力
  imagination: number; // 想象力
}
```

#### `packages/ui-components/` - 可复用组件库
- 测评游戏通用组件
- 数据可视化组件(ECharts封装)
- 报告模板组件

## 🗄️ 数据库架构

```
                    ┌─────────────────┐
                    │    用户/业务数据  │ MySQL 8.0
                    │ (users, classes) │
                    └────────┬────────┘
                             │
┌─────────────┐    ┌─────────▼─────────┐    ┌─────────────────┐
│ student-app  │───▶│  business-backend │───▶│  parent-app      │
└─────────────┘    └─────────┬─────────┘    └─────────────────┘
                              │
                              │ 非结构化数据
                              ▼
                    ┌─────────────────┐
                    │  用户行为/日志    │ MongoDB
                    │  (行为轨迹)      │
                    └────────┬────────┘
                             │
                    ┌────────▼─────────┐
                    │ gateway-backend   │ 高并发写入
                    └────────┬────────┘
                             │ 实时统计
                             ▼
                    ┌─────────────────┐
                    │  测评分析/常模    │ ClickHouse
                    │  (OLAP分析)     │
                    └────────┬────────┘
                             │
                    ┌────────▼─────────┐
                    │   ai-service      │ RAG/向量化
                    │   (LangChain)    │
                    └──────────────────┘
```

## 🔌 API 路由设计

| 服务 | 路由 | 端口 | 说明 |
|------|------|------|------|
| **Gateway (Go)** | `/api/v1/assessment/results` | 8081 | 游戏结果上报(高并发) |
| | `/api/v1/health` | 8081 | 健康检查 |
| **Business (Java)** | `/api/v1/users` | 8080 | 用户管理 |
| | `/api/v1/classes` | 8080 | 班级管理 |
| | `/api/v1/tasks` | 8080 | 测评任务 |
| | `/api/v1/reports` | 8080 | 报告查看 |
| **AI Service (Python)** | `/api/v1/analyze` | 8001 | 能力分析 |
| | `/api/v1/rag/query` | 8001 | 知识库检索 |
| | `/api/v1/reports/generate` | 8001 | 智能报告生成 |

## 🔄 数据流

### 1. 测评流程
```
学生端(PixiJS) ──游戏结果──▶ Go网关 ──实时写入──▶ ClickHouse
                    │                              │
                    │ 异步上报                      │ 分析
                    ▼                              ▼
              Java后端 ◀──── 任务数据 ◀──── Go网关
```

### 2. AI分析流程
```
测评结果 ──▶ ClickHouse ──统计分析──▶ AI Service
                                       │
                                       │ RAG检索
                                       ▼
                                  Milvus (知识库)
                                       │
                                       │ LLM推理
                                       ▼
                                   报告/建议
```

## ⚙️ 开发工具

### Turborepo 配置 (`turbo.json`)
```json
{
  "pipeline": {
    "build": { "dependsOn": ["^build"], "outputs": ["dist/**"] },
    "dev": { "cache": false },
    "test": { "dependsOn": ["build"] },
    "lint": {}
  }
}
```

### PNPM Workspace (`pnpm-workspace.yaml`)
```yaml
packages:
  - 'apps/*'
  - 'packages/*'
  - 'tools/*'
```

## 🚀 部署策略

### Docker Compose (开发环境)
```yaml
services:
  student-app:        # 前端
    build: ./apps/student-app
    ports: ["3000:3000"]
  parent-app:         # 前端  
    build: ./apps/parent-app
    ports: ["3001:3001"]
  teacher-app:        # 前端
    build: ./apps/teacher-app
    ports: ["3002:3002"]
  
  business-backend:   # Java
    build: ./apps/business-backend
    ports: ["8080:8080"]
    depends_on: [mysql, mongodb]
  
  gateway-backend:    # Go
    build: ./apps/gateway-backend
    ports: ["8081:8081"]
    depends_on: [clickhouse, redis]
  
  ai-service:         # Python
    build: ./apps/ai-service
    ports: ["8001:8001"]
    depends_on: [milvus]
```

### Kubernetes 部署
```
infra/k8s/
├── base/               # 公共配置
├── namespaces/         # 命名空间
├── services/           # Service 定义
│   ├── student/
│   ├── parent/
│   ├── teacher/
│   ├── business/
│   ├── gateway/
│   └── ai/
└── ingress/            # 路由配置
```

## 📊 服务健康检查端点

| 服务 | /health | /metrics |
|------|---------|----------|
| student-app | `/` | `/metrics` |
| parent-app | `/` | `/metrics` |
| teacher-app | `/` | `/metrics` |
| business-backend | `/actuator/health` | `/actuator/prometheus` |
| gateway-backend | `/health` | `/metrics` |
| ai-service | `/health` | `/metrics` |

## ⚡ 开发工作流

```bash
# 安装依赖
pnpm install

# 启动开发环境(全部)
pnpm dev

# 只启动指定服务
pnpm --filter student-app dev
pnpm --filter business-backend dev

# 构建所有
pnpm build

# 测试
pnpm test
```
