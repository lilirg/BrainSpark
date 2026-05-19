# 🧠 BrainSpark - 智启星

> 面向K12学生的游戏化认知能力测评与AI个性化成长建议平台

## 📋 项目简介

BrainSpark 是一个基于脑机接口理论的K12学生认知能力测评平台，通过精心设计的测评游戏和AI分析，为每个学生生成个性化的成长建议。

### 核心特性

- 🎮 **游戏化测评**: 6大认知维度（记忆/注意/逻辑/创造/观察/想象）
- 🤖 **AI智能分析**: 基于LangChain和RAG技术生成专业报告
- 👨‍👩‍👧 **多角色端**: 学生端(游戏)/家长端(查看)/教师端(管理)
- 📊 **实时分析**: ClickHouse OLAP处理百万级测评数据
- 🏗️ **Monorepo架构**: Turborepo + pnpm workspace统一管理

## 🏗️ 技术架构

```
BrainSpark/                          # 根目录 (Monorepo)
├── apps/                            # 独立部署的应用
│   ├── student-web/              # 学生端 (Vue 3 + PixiJS + WebGL)
│   ├── parent-web/               # 家长端 (Vue 3 + Element Plus)
│   ├── teacher-web/              # 教师端 (Vue 3 + Element Plus + ECharts)
│   ├── backend-business/         # 业务后端 (Java Spring Boot 3)
│   ├── backend-gateway/          # 高并发网关 (Go Gin)
│   └── ai-service/               # AI评估服务 (Python FastAPI + LangChain)
├── packages/                      # 共享包
│   ├── shared-types/             # TypeScript公共类型定义
│   ├── api-client/               # API客户端库
│   ├── eslint-config/            # ESLint统一配置
│   └── typescript-config/        # TypeScript共享配置
├── infrastructure/                # DevOps配置
│   ├── docker/                   # Docker Compose配置
│   ├── k8s/                      # Kubernetes部署
│   └── nginx/                    # Nginx反向代理
├── docs/                          # 项目文档
│   ├── scheme.md                 # 架构设计文档
│   ├── repo-structure.md         # 仓库结构说明
│   └── dev-guide/                # 开发指南
├── scripts/                       # 工具脚本
└── .github/workflows/            # CI/CD配置
```

## 🚀 快速开始

### 环境要求

- **基础环境**: Node.js >= 18.0, pnpm >= 8.0
- **后端开发**: Java 17+, Go 1.21+, Python 3.11+
- **数据库**: Docker (用于启动 MySQL/MongoDB/ClickHouse)

### 安装

```bash
# 克隆项目
git clone https://github.com/your-org/BrainSpark.git
cd BrainSpark

# 安装所有依赖
pnpm install
```

### 启动开发环境

```bash
# 一键启动所有服务
pnpm dev:all

# 或单独启动某个服务
pnpm --filter @brainspark/student dev      # 学生端 (localhost:3000)
pnpm --filter @brainspark/parent dev       # 家长端 (localhost:3001)
pnpm --filter @brainspark/teacher dev      # 教师端 (localhost:3002)
pnpm --filter backend-business dev         # 业务后端 (localhost:8080)
pnpm --filter backend-gateway dev          # Go网关 (localhost:8081)
pnpm --filter ai-service dev               # AI服务 (localhost:8001)
```

### 构建与测试

```bash
# 构建所有应用
pnpm build:all

# 运行所有测试
pnpm test:all

# 代码检查
pnpm lint
```

## 📚 服务说明

| 服务 | 端口 | 技术栈 | 说明 |
|------|------|--------|------|
| **Student Web** | 3000 | Vue3 + PixiJS | 游戏化测评引擎，支持WebGL 60fps渲染 |
| **Parent Web** | 3001 | Vue3 + Element Plus | 家长查看孩子成长报告的仪表板 |
| **Teacher Web** | 3002 | Vue3 + Element Plus | 班级管理、测评发起、报告审阅 |
| **Business Backend** | 8080 | Spring Boot 3 | 核心业务API (用户/班级/任务) |
| **Gateway** | 8081 | Go Gin | 高并发游戏结果收集网关 |
| **AI Service** | 8001 | FastAPI + LangChain | 能力分析、RAG检索、报告生成 |

## 💾 数据存储

| 数据库 | 用途 |
|--------|------|
| MySQL 8.0 | 用户、班级、任务等核心业务数据 |
| MongoDB | 用户行为轨迹、非结构化日志 |
| ClickHouse | 测评数据OLAP分析 |
| Milvus | 教育知识库向量存储 |
| Redis | 缓存、限流、Session |

## 🛠 开发规范

- 提交遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范
- 使用ESLint + Prettier统一代码风格
- 类型定义统一在 [`packages/shared-types`](packages/shared-types/) 中维护
- 所有API变更需同步更新 [`docs/api/`](docs/api/) 文档

## 📄 许可证

MIT License