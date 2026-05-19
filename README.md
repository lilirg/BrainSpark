# 🧠 BrainSpark - 智启星

> 面向K12学生的游戏化认知能力测评与AI个性化成长建议平台

## 📦 项目结构

```
BrainSpark/
├── apps/                          # 独立部署的应用
│   ├── student-web/              # 学生端 (Vue 3 + PixiJS)
│   ├── parent-web/               # 家长端 (Vue 3 + Element Plus)
│   ├── teacher-web/              # 教师端 (Vue 3 + Element Plus)
│   ├── backend-business/         # 业务后端 (Java Spring Boot 3)
│   ├── backend-gateway/          # 高并发网关 (Go)
│   └── ai-service/               # AI评估服务 (Python FastAPI)
├── packages/                      # 共享包
│   ├── shared-types/             # 公共类型定义
│   ├── api-client/               # API客户端
│   ├── eslint-config/            # ESLint配置
│   └── typescript-config/        # TypeScript配置
├── infrastructure/                # DevOps配置
│   ├── docker/                   # Docker配置
│   ├── k8s/                      # K8s部署配置
│   └── nginx/                    # Nginx配置
├── docs/                          # 项目文档
├── scripts/                       # 工具脚本
└── .github/workflows/            # CI/CD配置
```

## 🚀 快速开始

### 前置要求

- Node.js >= 18.0.0
- pnpm >= 8.0.0
- Docker & Docker Compose
- Java 17+ (开发后端)
- Go 1.21+ (开发网关)
- Python 3.11+ (开发AI服务)

### 安装

```bash
# 安装所有依赖
pnpm install

# 或仅安装特定应用
pnpm install --filter=apps/student-web
```

### 开发

```bash
# 启动所有服务（开发模式）
pnpm run dev:all

# 启动单个服务
pnpm run dev:student      # 学生端
pnpm run dev:parent       # 家长端
pnpm run dev:teacher      # 教师端
pnpm run dev:business     # 业务后端
pnpm run dev:gateway      # 网关
pnpm run dev:ai           # AI服务
```

### 构建

```bash
# 构建所有应用
pnpm run build:all

# 构建单个应用
pnpm run build:student
```

### 测试

```bash
# 运行所有测试
pnpm run test:all

# 运行单个测试
cd apps/student-web && pnpm test
```

## 🛠 技术栈

| 模块 | 技术栈 |
|------|--------|
| 学生端 | Vue 3 + TypeScript + Vite + PixiJS |
| 家长/教师端 | Vue 3 + TypeScript + Vite + Element Plus |
| 业务后端 | Java 17 + Spring Boot 3 + MyBatis Plus |
| 游戏网关 | Go + Gin + Kafka |
| AI服务 | Python 3.11 + FastAPI + LangChain |
| 数据库 | MySQL + MongoDB + Redis + Milvus |

## 📖 文档

- [架构设计](docs/scheme.md)
- [开发指南](docs/dev-guide/README.md)
- [API文档](docs/api/README.md)

## 🔧 开发规范

- 使用 TypeScript 类型定义包 [`packages/shared-types`](packages/shared-types/)
- 所有前端代码遵循 ESLint + Prettier 规范
- 提交信息遵循 Conventional Commits 规范

## 📄 License

MIT