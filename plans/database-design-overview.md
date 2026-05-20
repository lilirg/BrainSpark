# BrainSpark 数据库设计概览

> 版本: 1.0 | 最后更新: 2026-05-20 | 基于 [`docs/architecture/data-model.md`](../docs/architecture/data-model.md)

## 一、数据库架构总览

BrainSpark 采用 **多数据库协同架构**，根据不同业务场景选择合适的存储引擎：

```mermaid
graph LR
    subgraph 事务型存储
        MySQL[(MySQL 8.0<br/>核心业务数据)]
    end
    
    subgraph 文档型存储
        MongoDB[(MongoDB 7<br/>行为事件日志)]
    end
    
    subgraph 分析型存储
        ClickHouse[(ClickHouse<br/>OLAP 分析)]
    end
    
    subgraph 缓存/队列
        Redis[(Redis 7<br/>缓存/锁/限流)]
    end
    
    subgraph 向量存储
        Milvus[(Milvus 2<br/>RAG 知识库)]
    end
    
    UserFrontend[学生/家长/教师端] -->|HTTPS| GoGateway[Go 网关]
    GoGateway --> MySQL
    GoGateway --> Redis
    StudentEngine[PixiJS 测评引擎] -->|WebSocket| GoGateway
    StudentEngine -->|批量事件| MongoDB
    BackendService[Java 业务服务] --> MySQL
    BackendService --> MongoDB
    BackendService --> Redis
    BackendService --> ClickHouse
    AIEngine[Python AI 服务] --> Milvus
    AIEngine --> MySQL
    BackendService --> AIEngine
```

## 二、MySQL 数据库设计

### 2.1 数据库分库策略

| 数据库名 | 用途 | 包含模块 |
|----------|------|----------|
| `users_schema` | 用户与合规数据 | 用户、家庭绑定、监护人同意 |
| `assessment_schema` | 测评业务数据 | 学生、班级、测评任务、会话、结果 |
| `mall_schema` | 商城与订单数据 | 商品、订单、订阅 |
| `ai_schema` | AI 服务数据 | 知识库、报告 |

### 2.2 核心 ER 关系图

```mermaid
erDiagram
    USER ||--o{ FAMILY_BINDING : has
    USER ||--o{ STUDENT_PROFILE : contains
    USER ||--o{ CLASS_MEMBER : joins
    USER ||--o{ ASSESSMENT_RESULT : completes
    USER ||--o{ ORDER : places
    
    ORGANIZATION ||--o{ CLASS : owns
    CLASS ||--o{ CLASS_MEMBER : has
    
    STUDENT_PROFILE ||--o{ ASSESSMENT_RESULT : takes
    ASSESSMENT_TYPE ||--o{ ASSESSMENT_TASK : defines
    
    ASSESSMENT_TASK ||--o{ TASK_ASSIGNMENT : distributes
    TASK_ASSIGNMENT ||--o{ STUDENT_TASK_ASSIGNMENT : assigned-to
    
    ASSESSMENT_RESULT ||--o{ REPORT : generates
    
    ORDER ||--o{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : referenced
    SUBSCRIPTION_PLAN ||--o{ SUBSCRIPTION : defines

    USER {
        BIGINT id PK
        VARCHAR username
        VARCHAR role
        VARCHAR real_name
        JSON extra_info
    }
    
    STUDENT_PROFILE {
        BIGINT id PK
        VARCHAR name_hash
        YEAR birth_year
        VARCHAR classroom_code
    }
    
    ASSESSMENT_TASK {
        BIGINT id PK
        VARCHAR type_code
        JSON config
        INT difficulty
    }
    
    ASSESSMENT_RESULT {
        BIGINT id PK
        BIGINT user_id
        JSON score_data
        JSON cognitive_profile
    }
    
    ORDER {
        BIGINT id PK
        VARCHAR order_no
        BIGINT user_id
        INT amount_cents
    }
```

### 2.3 MySQL 表清单

| 表名 | 所在库 | 说明 | 关键字段 |
|------|--------|------|----------|
| [`users`](docs/architecture/data-model.md#users-用户表) | users_schema | 用户表 | id, username, role, extra_info |
| [`family_bindings`](docs/architecture/data-model.md#family_bindings-家长学生关联表) | users_schema | 家长学生关联 | parent_user_id, student_user_id |
| [`guardian_consent`](docs/architecture/data-model.md#guardian_consent-监护人同意表) | users_schema | 监护人同意 | guardian_user_id, consent_given |
| [`students`](docs/architecture/data-model.md#students-学生信息表) | assessment_schema | 学生信息 | name_hash, birth_year |
| [`classes`](docs/architecture/data-model.md#classes-班级表) | assessment_schema | 班级表 | org_id, name, grade |
| [`class_members`](docs/architecture/data-model.md#class_members-班级成员表) | assessment_schema | 班级成员 | class_id, user_id, role |
| [`assessment_types`](docs/architecture/data-model.md#assessment_types-测评类型表) | assessment_schema | 测评类型 | code, cognitive_dimension |
| [`assessment_tasks`](docs/architecture/data-model.md#assessment_tasks-测评任务表) | assessment_schema | 测评任务 | type_code, config |
| [`task_assignments`](docs/architecture/data-model.md#task_assignments-任务分发表) | assessment_schema | 任务分发 | task_code, class_room_code |
| [`student_task_assignments`](docs/architecture/data-model.md#student_task_assignments-学生任务分发表) | assessment_schema | 学生任务分发 | assignment_id, student_id, status |
| [`assessment_sessions`](docs/architecture/data-model.md#assessment_sessions-测评会话表) | assessment_schema | 测评会话 | session_id, task_code, grid_size |
| [`event_summaries`](docs/architecture/data-model.md#event_summaries-事件汇总表) | assessment_schema | 事件汇总 | session_id, event_type |
| [`assessment_results`](docs/architecture/data-model.md#assessment_results-测评结果表) | assessment_schema | 测评结果 | user_id, score_data, cognitive_profile |
| [`products`](docs/architecture/data-model.md#products-商品表) | mall_schema | 商品 | sku_code, price_cents |
| [`orders`](docs/architecture/data-model.md#orders-订单表) | mall_schema | 订单 | order_no, payment_channel |
| [`subscription_plans`](docs/architecture/data-model.md#subscription_plans-订阅方案表) | mall_schema | 订阅方案 | plan_type, price_cents |
| [`knowledge_base`](docs/architecture/data-model.md#knowledge_base-知识库表) | ai_schema | 知识库 | doc_id, category |
| [`reports`](docs/architecture/data-model.md#reports-报告表) | ai_schema | 报告 | result_id, report_json |

## 三、ClickHouse 分析型数据库

### 3.1 表清单

| 表名 | 引擎 | 排序键 | 说明 |
|------|------|--------|------|
| [`assessment_event_records`](docs/architecture/data-model.md#21-assessment_event_records-用户原始测评事件表) | MergeTree | user_id, created_at | 原始行为事件 |
| [`assessment_results_agg`](docs/architecture/data-model.md#22-assessment_results_agg-用户测评结果聚合表) | MergeTree | user_id, started_at | 用户测评结果聚合 |
| [`cognitive_normalize`](docs/architecture/data-model.md#23-cognitive_normalize-教育常模表) | MergeTree | dimension, age_group | 教育常模数据 |
| [`education_knowledge`](docs/architecture/data-model.md#24-education_knowledge-教育知识表) | MergeTree | category, created_at | 教育知识 |
| [`normalize_version`](docs/architecture/data-model.md#25-normalize_version-常模版本管理表) | MergeTree | id | 常模版本管理 |

### 3.2 数据流向

```
学生端 PixiJS → WebSocket → Go 网关 → MongoDB (原始事件)
                                          ↓
                                    Flink/ETL 聚合
                                          ↓
                               ClickHouse (聚合结果)
                                          ↓
                              Java 服务读取分析
```

## 四、MongoDB 文档数据库

| 集合名 | 说明 | 关键索引 |
|--------|------|----------|
| [`event_records`](docs/architecture/data-model.md#31-event_records-事件记录集合) | 用户行为事件 | user_id+session_id, created_at (TTL 30 天) |

### 文档结构示例

```javascript
{
    _id: ObjectId,
    event_id: "event-xxxxx",
    user_id: NumberLong(12345),
    session_id: "session-yyyyy",
    type_code: "VISUAL_ATTENTION",
    event_type: "CLICK | HOVER | KEY_DOWN",
    performance_now: 1234567.890123,    // 微秒级精度
    reaction_time_ms: 420,
    pointer_x: 450,
    pointer_y: 320,
    device_info: {                       // 设备信息
        screen_width: 1920,
        pixel_ratio: 2.0,
    },
    created_at: ISODate(...)
}
```

## 五、Redis 缓存设计

### 5.1 Key 设计规范

| Key 模式 | 类型 | TTL | 用途 |
|----------|------|-----|------|
| `jwt:whitelist:<jti>` | String | Token 有效期 | 有效 JWT 令牌 |
| `jwt:blacklist:<jti>` | String | Token 有效期 | 吊销 JWT 令牌 |
| `session:user:<user_id>` | JSON | 30 天 | 用户会话信息 |
| `rate_limit:gateway:<ip>` | Counter | 60 秒 | IP 限流 |
| `report:pending:<user_id>` | String | 5 分钟 | 报告生成防重 |
| `assessment:lock:<session_id>` | JSON | 15 分钟 | 测评会话锁 |

### 5.2 限流策略

| 层级 | 阈值 | 时间窗口 |
|------|------|----------|
| IP 级别 | 500 QPS | 60 秒 |
| API 级别 | 100 QPS | 60 秒 |

## 六、Milvus 向量数据库

| 配置项 | 值 | 说明 |
|--------|-----|------|
| Collection | `brainspark_knowledge` | 教育知识库 |
| 向量维度 | 1536 | 适配 OpenAI embedding |
| 索引类型 | HNSW | M=16, efConstruction=256 |
| 度量类型 | IP (内积) | 相似度计算 |
| Top-K | 5 | 默认检索结果 |

## 七、存储角色分配

| 数据库 | 写 | 读 | 主要服务 |
|--------|-----|-----|----------|
| MySQL | Java 后端 | Java 后端 | 用户、订单、报告 |
| MongoDB | Go 网关 | Java 后端 | 行为事件流 |
| ClickHouse | ETL/Flink | Java/AI 服务 | OLAP 分析 |
| Redis | 全部服务 | 全部服务 | 缓存/锁/限流 |
| Milvus | Python AI | Python AI | RAG 检索 |

## 八、设计评价与优化建议

### 已完成 ✅

| 模块 | 状态 | 备注 |
|------|------|------|
| MySQL 事务表设计 | ✅ 完整 | 用户、测评、订单等核心表 |
| 索引设计 | ✅ 完整 | 覆盖常用查询路径 |
| ClickHouse 分析表 | ✅ 完整 | 行为记录、常模对比 |
| MongoDB 事件存储 | ✅ 完整 | 含 TTL 自动清理 |
| Redis 缓存策略 | ✅ 完整 | 会话、限流、防重 |
| Milvus 向量库 | ✅ 完整 | RAG 知识库 |
| 数据流向图 | ✅ 完整 | 各 DB 间数据流转 |

### 待优化建议 📋

| 序号 | 优化项 | 建议 | 优先级 |
|------|--------|------|--------|
| 1 | 分库分表策略 | `assessment_results` 按时间分区分表，预计日增 10 万+ | 中 |
| 2 | 学生登录方案 | [`students.name_hash`](docs/architecture/data-model.md#students-学生信息表) 当前用姓名哈希登录，建议增加 `student_code` 学号方案 | 中 |
| 3 | 常模数据更新机制 | `cognitive_normalize` 需设计周期性批处理作业更新统计数据 | 低 |
| 4 | 行为数据归档 | MongoDB 30 天 TTL 后数据需归档至 ClickHouse 或 OSS | 高 |
| 5 | 软删除统一 | 核心业务表增加 `deleted_at` 字段，支持数据恢复 | 中 |
| 6 | 审计日志 | 增加 `audit_logs` 表追踪数据变更历史 | 低 |
| 7 | Flyway 迁移脚本 | 需根据此设计生成版本化 SQL 迁移文件 | 高 |

## 九、数据字典索引

```
├── docs/architecture/data-model.md          ← 数据模型黄金源 (全文档)
├── docs/services/backend-business.md        ← Java 后端实体关系图
├── docs/services/ai-service.md              ← AI 服务数据依赖
├── docs/services/backend-gateway.md         ← 网关数据存储
├── docs/services/data-engine.md             ← ClickHouse / ETL 设计
└── docs/quality/security-design.md          ← 数据安全设计
```

---

> **维护指南**: 新增表请同步更新 [`docs/architecture/data-model.md`](docs/architecture/data-model.md)，保持数据模型一致性。
