# 🧠 BrainSpark - 智启星

> 面向K12学生的游戏化认知能力测评与AI个性化成长建议平台

## 📋 项目简介

BrainSpark 是一个基于认知科学理论的K12学生认知能力测评平台，通过精心设计的测评游戏和AI分析，为每个学生生成个性化的成长建议。

### 核心特性

- 🎮 **游戏化测评**: 6大认知维度（记忆/注意/逻辑/创造/观察/想象）
- 🤖 **AI智能分析**: 基于 LangChain 和 RAG 技术生成专业报告
- 👨‍👩‍👧 **多角色端**: 学生端(游戏) / 家长端(查看) / 教师端(管理) / 运营端(后台)
- 📊 **实时分析**: ClickHouse OLAP 处理百万级测评数据
- 🏗️ **Monorepo架构**: Turborepo + pnpm workspaces 统一管理

## 🏗️ 技术架构

```
BrainSpark/                              # 根目录 (Monorepo)
├── apps/                                    # 独立部署的应用
│   ├── student-web/                     # 学生端 (Vue 3 + PixiJS + WebGL)
│   ├── parent-web/                      # 家长端 (Vue 3 + Element Plus + ECharts)
│   ├── teacher-web/                     # 教师端 (Vue 3 + Element Plus + ECharts)
│   ├── operator-web/                    # 运营端 (Vue 3 + Element Plus)
│   ├── backend-business/                # 业务后端 (Java Spring Boot 3)
│   ├── backend-gateway/                 # 高并发网关 (Go Gin)
│   └── ai-service/                      # AI评估服务 (Python FastAPI + LangChain)
├── packages/                              # 共享包
│   ├── shared-types/                    # TypeScript 公共类型定义
│   ├── api-client/                      # API 客户端库
│   ├── eslint-config/                   # ESLint 统一配置
│   └── typescript-config/               # TypeScript 共享配置
├── docs/                                  # 项目文档
│   ├── product/                         # 产品设计文档
│   ├── architecture/                    # 架构设计文档
│   ├── frontend/                        # 前端开发指南
│   ├── services/                        # 后端服务文档
│   ├── infrastructure/                  # 基础设施文档
│   ├── quality/                         # 质量保障文档
│   └── operations/                      # 运维文档
```

## 🛠 技术栈

| 类别 | 技术 |
|------|------|
| 学生端 | Vue 3 + TypeScript + Vite + PixiJS |
| 家长/教师/运营端 | Vue 3 + TypeScript + Element Plus + ECharts |
| 业务后端 | Java 17 + Spring Boot 3 |
| 高并发网关 | Go 1.21 + Gin |
| AI 服务 | Python 3.11 + FastAPI + LangChain |
| 数据库 | MySQL 8.0 + MongoDB + ClickHouse + Redis + Milvus |

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
# 一键启动所有前端服务
pnpm dev:all

# 或单独启动某个前端应用
pnpm dev:student        # 学生端 (localhost:3000)
pnpm dev:parent         # 家长端 (localhost:3001)
pnpm dev:teacher        # 教师端 (localhost:3002)
pnpm dev:operator       # 运营端 (localhost:3003)
```

> **重要**: 后端服务**不能**通过 `pnpm dev:all` 启动，需分别进入对应目录手动启动：
> ```bash
> cd apps/backend-business && mvn spring-boot:run    # 业务后端 :8080
> cd apps/backend-gateway && go run main.go           # 网关 :8081
> cd apps/ai-service && uvicorn main:app --reload     # AI 服务 :8001
> ```

### 构建与测试

```bash
# 构建所有前端应用
pnpm build:all

# 运行所有测试
pnpm test:all

# 代码检查
pnpm lint:all

# 类型检查
pnpm typecheck:all
```

## 📚 服务说明

| 服务 | 端口 | 技术栈 | 说明 |
|------|------|--------|------|
| **Student Web** | 3000 | Vue3 + PixiJS | 游戏化测评引擎，支持 WebGL 60fps 渲染 |
| **Parent Web** | 3001 | Vue3 + Element Plus | 家长查看孩子成长报告的仪表板 |
| **Teacher Web** | 3002 | Vue3 + Element Plus | 班级管理、测评发起、报告审阅 |
| **Operator Web** | 3003 | Vue3 + Element Plus | 运营管理后台 |
| **Business Backend** | 8080 | Spring Boot 3 | 核心业务API (用户/班级/任务) |
| **Gateway** | 8081 | Go Gin | 高并发游戏结果收集网关 |
| **AI Service** | 8001 | FastAPI + LangChain | 能力分析、RAG检索、报告生成 |

## 💾 数据存储

| 数据库 | 用途 |
|--------|------|
| MySQL 8.0 | 用户、班级、任务等核心业务数据 |
| MongoDB | 用户行为轨迹、非结构化日志 |
| ClickHouse | 测评数据 OLAP 分析 |
| Milvus | 教育知识库向量存储 |
| Redis | 缓存、限流、Session |

## 📚 文档

| 文档 | 路径 |
|------|------|
| 产品设计 | [`docs/product/`](docs/product/) |
| 架构设计 | [`docs/architecture/`](docs/architecture/) |
| 前端开发 | [`docs/frontend/`](docs/frontend/) |
| 后端服务 | [`docs/services/`](docs/services/) |
| 基础设施 | [`docs/infrastructure/`](docs/infrastructure/) |
| 质量保障 | [`docs/quality/`](docs/quality/) |
| 运维手册 | [`docs/operations/`](docs/operations/) |

## 🛠 开发规范

- 提交遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范
- 使用 ESLint + Prettier 统一代码风格
- 类型定义统一在 [`packages/shared-types`](packages/shared-types/) 中维护
- 所有 API 变更需同步更新 [`docs/architecture/api-contract.md`](docs/architecture/api-contract.md)

## 📄 许可证

MIT License