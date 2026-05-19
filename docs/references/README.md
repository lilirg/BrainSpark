# 参考资料文档

本目录包含 BrainSpark 的命名规范、术语表等技术参考资料。

## 文档列表

| 文件名 | 说明 | 状态 |
|--------|------|------|
| `naming-conventions.md` | 命名规范 | 待创建 |
| `glossary.md` | 术语表 | 待创建 |

## 命名规范概览

### 服务命名

| 应用 | 目录名 | API前缀 |
|------|--------|---------|
| 学生端 | `apps/student-web` | `/api/v1/student` |
| 家长端 | `apps/parent-web` | `/api/v1/parent` |
| 教师端 | `apps/teacher-web` | `/api/v1/teacher` |
| 运营端 | `apps/operator-web` | `/api/v1/operator` |
| 后端网关 | `apps/backend-gateway` | `/api/v1/` |
| 业务后端 | `apps/backend-business` | `/api/v1/` |
| AI服务 | `apps/ai-service` | `/api/v1/ai` |

### 目录命名

| 类别 | 格式 | 示例 |
|------|------|------|
| 前端应用 | `{role}-web` | `student-web`, `parent-web` |
| 后端服务 | `{role}-{type}` | `backend-business`, `backend-gateway` |
| 共享包 | `packages/*` | `shared-types`, `shared-utils` |

## 核心术语

| 术语 | 英文 | 说明 |
|------|------|------|
| 认知能力 | Cognitive Ability | 注意力、记忆力、逻辑思维等底层能力 |
| 常模 | Norm | 标准化测试的参照群体数据 |
| RAG | Retrieval-Augmented Generation | 检索增强生成技术 |
| PIPL | Personal Information Protection Law | 个人信息保护法 |
| MVP | Minimum Viable Product | 最小可行产品 |

---

> 本文档为参考资料目录入口文件，创建于 2026-05-19。