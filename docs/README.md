# BrainSpark 文档中心

> 文档索引与导航入口 | 创建于 2026-05-19

---

## 快速导航

| 类别 | 目录 | 说明 |
|------|------|------|
| 🏗️ 架构 | [architecture](./architecture/) | 核心架构定义、API契约、数据模型 |
| 🔧 服务 | [services](./services/) | 各后端服务设计文档 |
| 🎨 前端 | [frontend](./frontend/) | 所有前端应用设计文档 |
| 🏢 基础设施 | [infrastructure](./infrastructure/) | 部署、监控、CI/CD设计 |
| ✅ 质量 | [quality](./quality/) | 测试架构与安全设计 |
| 📈 运营 | [operations](./operations/) | 迁移策略与升级规划 |
| 📜 产品 | [product](./product/) | 产品策划、计划、仓库结构 |
| 📚 参考 | [references](./references/) | 命名规范、术语表 |

---

## 文档结构

```
docs/
├── README.md                         📑 本文件 - 文档总览
│
├── architecture/                     🏗️ 架构层
│   ├── README.md                     入口文件
│   ├── api-contract.md               API 契约
│   └── data-model.md                 数据模型
│
├── services/                         🔧 服务设计
│   ├── README.md                     入口文件
│   ├── backend-business.md           业务后端设计
│   ├── backend-gateway.md            网关层设计
│   ├── ai-service.md                 AI服务设计
│   └── data-engine.md                数据引擎设计
│
├── frontend/                         🎨 前端设计
│   ├── README.md                     入口文件
│   ├── student-web.md                学生端设计
│   ├── parent-web.md                 家长端设计
│   ├── teacher-web.md                教师端设计
│   └── operator-web.md               运营端设计
│
├── infrastructure/                   🏢 基础设施
│   ├── README.md                     入口文件
│   ├── deployment.md                 部署架构
│   ├── ci-cd.md                      CI/CD 设计
│   └── monitoring.md                 监控告警
│
├── quality/                          ✅ 质量保障
│   ├── README.md                     入口文件
│   ├── test-design.md                测试架构
│   └── security-design.md            安全架构
│
├── operations/                       📈 运营与迁移
│   ├── README.md                     入口文件
│   └── migration-design.md           迁移与升级策略
│
├── product/                          📜 产品参考
│   ├── README.md                     入口文件
│   ├── scheme.md                     产品立项文档
│   ├── repo-structure.md             仓库结构文档
│   └── plan.md                       项目计划文档
│
├── references/                       📚 参考资料
│   ├── README.md                     入口文件
│   ├── naming-conventions.md          命名规范
│   └── glossary.md                   术语表
│
└── 根目录文件（精简保留）
    └── optimization-plan.md          优化方案（按需查阅）
```

---

## 目录详情

### 🏗️ architecture - 架构层

集中核心架构定义，建立唯一信息源。

- `api-contract.md` - API 契约
- `data-model.md` - 数据模型

### 🔧 services - 服务设计

按服务域划分后端设计。

- `backend-business.md` - 业务后端
- `backend-gateway.md` - 网关层
- `ai-service.md` - AI服务
- `data-engine.md` - 数据引擎

### 🎨 frontend - 前端设计

统一前端设计归类。

- `student-web.md` - 学生端
- `parent-web.md` - 家长端
- `teacher-web.md` - 教师端
- `operator-web.md` - 运营端

### 🏢 infrastructure - 基础设施

集中部署、监控配置。

- `deployment.md` - 部署架构
- `ci-cd.md` - CI/CD 设计
- `monitoring.md` - 监控告警

### ✅ quality - 质量保障

整合测试和安全设计。

- `test-design.md` - 测试架构
- `security-design.md` - 安全架构

### 📈 operations - 运营与迁移

迁移与升级策略。

- `migration-design.md` - 迁移与升级策略

### 📜 product - 产品参考

产品相关参考文档。

- `scheme.md` - 产品立项
- `repo-structure.md` - 仓库结构
- `plan.md` - 项目计划

### 📚 references - 参考资料

辅助参考信息。

- `naming-conventions.md` - 命名规范
- `glossary.md` - 术语表

---

## 文档使用指南

### 查阅顺序建议

1. **新用户**：从 `product/scheme.md` 了解产品背景
2. **前端开发**：进入 `frontend/` 目录查看对应前端设计
3. **后端开发**：查看 `services/` 目录下对应服务文档
4. **运维人员**：参考 `infrastructure/` 部署文档
5. **测试/QA**：关注 `quality/` 测试架构文档

### 黄金源规则

为保证文档一致性，请遵循引用规则：

| 内容类型 | 查询源 |
|---------|--------|
| API 路由 | [`architecture/api-contract.md`](./architecture/api-contract.md) |
| 数据库 DDL | [`architecture/data-model.md`](./architecture/data-model.md) |
| Kafka Topics | [`services/data-engine.md`](./services/data-engine.md) |
| JWT/认证 | [`quality/security-design.md`](./quality/security-design.md) |

---

## 文档规范

- 使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式
- 技术术语首次出现需提供中英文标注
- 所有代码路径使用 [`filename`](relative/path) 格式
- 图表优先使用 Mermaid.js

---

> 📋 **下一步**: 文档结构化已完成，相应源文档已移动到对应的子目录中。

---

*BrainSpark 文档中心 - 版本 1.0.0 | 更新于 2026-05-19*
