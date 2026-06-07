# PROJECT-NOTES.md

> 项目发现笔记 - BrainSpark 项目

## 非显而易见的项目发现

### 包名不一致
- `@brain-spark/*`（student-web, parent-web, shared-types）vs `@brainspark/*`（teacher-web, operator-web）
- Java 包名：`com.braSpark`（注意大小写，非 `com.brainspark`）

### 构建注意事项
- [`turbo.json`](turbo.json:13): `test` 依赖 `build`，运行测试前必须先构建
- 后端服务（backend-business, backend-gateway, ai-service）需分别进入对应目录启动，**不能**通过 `turbo dev` 启动
- [`pnpm-workspace.yaml`](pnpm-workspace.yaml:4): 包含 `infrastructure/*`（非仅 apps/* 和 packages/*）

### Go 网关
- 入口为 [`main.go`](apps/backend-gateway/main.go)（非文档所述的 `cmd/server/main.go`）
- [`RateLimiter`](apps/backend-gateway/internal/middleware/middleware.go:27) 为内存实现（非 Redis），每分钟每 IP 100 次
- [`RequestID`](apps/backend-gateway/internal/middleware/middleware.go:55) 使用时间戳生成（非 UUID）

### AI 服务
- [`MilvusVectorStore`](apps/ai-service/app/rag/vector_store.py:5) 使用单例模式（`__new__` 实现）
- 默认 LLM 模型为 `gpt-4o`，支持自定义 `OPENAI_BASE_URL`

### 前端差异
- 学生端使用 PixiJS（无 Element Plus），家长/教师/运营端使用 Element Plus
- [`parent-web`](apps/parent-web/src/main.ts:13) 注册了所有 Element Plus 图标（全局注册）
- 教师端使用 ESLint 9 + Prettier，其他前端使用 ESLint 8 + vitest

### 共享类型
- [`shared-types`](packages/shared-types/src/assessment.ts) 定义 3 种测评类型：`SCHULTE_GRID`、`NUMBER_SPAN`、`PATTERN_RECOGNITION`
- [`CapabilityRadar`](packages/shared-types/src/report.ts) 包含 6 个维度：attention, memory, logic, language, spatial, executiveFunction

### 关键命令
```bash
# 安装全部依赖
pnpm install

# 启动前端（通过 turbo）
pnpm dev:student        # 学生端 :3000
pnpm dev:parent         # 家长端 :3001
pnpm dev:teacher        # 教师端 :3002

# 启动后端（需进入目录）
cd apps/backend-business && mvn spring-boot:run    # :8080
cd apps/backend-gateway && go run main.go           # :8081
cd apps/ai-service && uvicorn main:app --reload     # :8001

# 构建与测试
pnpm build:all          # 全量构建
pnpm test:all           # 运行所有测试（需先 build）
pnpm lint:all           # 代码检查
pnpm typecheck:all      # 类型检查