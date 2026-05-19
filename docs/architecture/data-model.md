# BrainSpark 数据模型黄金源

> **用途**: 统一管理 BrainSpark 平台所有数据库、缓存和向量存储的表结构设计，作为数据模型的唯一参考源。
> 
> **最后更新日期**: 2026-05-19
> 
> **维护者**: BrainSpark 架构团队
> 
> **数据来源**:
> - [`docs/business-backend-design.md`](../business-backend-design.md) - MySQL DDL、MongoDB 集合
> - [`docs/data-engine-design.md`](../data-engine-design.md) - ClickHouse 分析表、Milvus 配置
> - [`docs/infrastructure-design.md`](../infrastructure-design.md) - 业务库 DDL、Redis 设计

---

## 目录

1. [MySQL 数据库表](#1-mysql-数据库表)
   - 1.1 用户与合规库 (users_schema)
   - 1.2 测评业务库 (assessment_schema)
   -1.3 商城与订单库 (mall_schema)
   - 1.4 AI 服务库 (ai_schema)
2. [ClickHouse 分析型数据库](#2-clickhouse-分析型数据库)
3. [MongoDB 文档数据库](#3-mongodb-文档数据库)
4. [Redis 缓存](#4-redis-缓存)
5. [Milvus 向量数据库](#5-milvus-向量数据库)

---

## 1. MySQL 数据库表

### 1.1 用户与合规库 (users_schema)

#### users (用户表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| username | VARCHAR(50) | NOT NULL, UNIQUE | 用户名 |
| password_hash | VARCHAR(255) | NOT NULL | BCrypt 加密密码 |
| role | VARCHAR(20) | NOT NULL | 角色：ADMIN, TEACHER, STUDENT, PARENT, OPERATOR |
| real_name | VARCHAR(50) | - | 真实姓名 |
| avatar | VARCHAR(255) | - | 头像 URL |
| phone | VARCHAR(20) | - | 手机号 |
| email | VARCHAR(100) | - | 邮箱 |
| status | VARCHAR(20) | DEFAULT 'ACTIVE' | 状态：ACTIVE, DISABLED, PENDING_VERIFY |
| extra_info | JSON | - | 额外属性（年龄、年级等） |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

**索引**: `idx_username(username)`, `idx_role(role)`, `idx_status(status)`

---

#### family_bindings (家长学生关联表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| parent_user_id | BIGINT | NOT NULL | 家长用户 ID |
| student_user_id | BIGINT | NOT NULL | 学生用户 ID |
| binding_time | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 绑定时间 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否有效 |

**索引**: `idx_parent(parent_user_id)`, `idx_student(student_user_id)`, `uk_family(parent_user_id, student_user_id)`

---

#### guardian_consent (监护人同意表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| guardian_user_id | BIGINT | NOT NULL | 监护人用户 ID |
| child_user_id | BIGINT | NOT NULL | 儿童用户 ID |
| consent_given | TINYINT | DEFAULT 0 | 是否已同意 (0/1) |
| consent_at | TIMESTAMP | NULL | 同意时间 |
| consent_method | VARCHAR(20) | - | 同意方式：WEB_FORM, PAPER_SCANNED |
| consent_proof | VARCHAR(255) | - | 证明文件路径 |
| is_active | TINYINT | DEFAULT 1 | 是否有效 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引**: `uk_guardian_child(guardian_user_id, child_user_id)`, `idx_consent_given(consent_given)`

---

### 1.2 测评业务库 (assessment_schema)

#### students (学生信息表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| real_name | VARCHAR(32) | - | 真实姓名（服务端脱敏显示） |
| name_hash | VARCHAR(64) | UNIQUE NOT NULL | 姓名哈希值，用于登录查询 |
| birth_year | YEAR | - | 出生年份（仅用于年龄分组） |
| gender | TINYINT | - | 性别：1-男, 2-女, 0-未知 |
| classroom_code | VARCHAR(20) | - | 班级标识 |
| school_name | VARCHAR(128) | - | 学校名称 |
| parent_guardian_name | VARCHAR(64) | - | 家长/监护人姓名 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引**: `idx_birth_year(birth_year)`, `idx_classroom(classroom_code)`

---

#### parents (家长账号表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| account_id | BIGINT | NOT NULL | 关联 account_users |
| child_student_id | BIGINT | NOT NULL | 关联学生 |
| relationship | VARCHAR(20) | - | 关系：PARENT_GUARDIAN, TEACHER_OBSERVER |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引**: `uk_account(account_id)`, `uk_child(child_student_id)`

---

#### classes (班级表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| org_id | BIGINT | - | 机构 ID |
| name | VARCHAR(100) | NOT NULL | 班级名称 |
| grade | VARCHAR(20) | - | 年级 |
| description | TEXT | - | 班级描述 |
| teacher_id | BIGINT | - | 班主任用户 ID |
| max_students | INT | DEFAULT 50 | 最大学生数 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否有效 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

---

#### class_members (班级成员表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| class_id | BIGINT | NOT NULL | 班级 ID |
| user_id | BIGINT | NOT NULL | 用户 ID |
| role | VARCHAR(20) | - | 角色：STUDENT, TEACHER |
| joined_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 加入时间 |

**索引**: `uk_class_member(class_id, user_id)`

---

#### assessment_types (测评类型表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| code | VARCHAR(50) | NOT NULL, UNIQUE | 编码：SCHULTER, DIGITAL_SPAN, PATTERN_REASONING |
| name | VARCHAR(100) | NOT NULL | 测评名称 |
| description | TEXT | - | 描述 |
| cognitive_dimension | VARCHAR(50) | - | 认知维度：VISUAL, AUDITORY, MEMORY, LOGIC |
| duration_seconds | INT | - | 时长(秒) |
| version | VARCHAR(20) | - | 版本号 |
| config | JSON | - | 测评参数配置 |
| is_published | BOOLEAN | DEFAULT FALSE | 是否已发布 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

---

#### assessment_tasks (测评任务表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| org_id | BIGINT | - | 机构 ID |
| class_id | BIGINT | - | 班级 ID |
| title | VARCHAR(200) | NOT NULL | 任务标题 |
| type_code | VARCHAR(50) | NOT NULL | 测评类型编码 |
| config | JSON | - | 任务配置（难度、顺序、白/黑卡） |
| difficulty | INT | DEFAULT 1 | 难度等级 |
| duration_min | INT | DEFAULT 10 | 时长(分钟) |
| assigned_at | TIMESTAMP | NULL | 分配时间 |
| start_at | TIMESTAMP | NULL | 开始时间 |
| end_at | TIMESTAMP | NULL | 截止时间 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否有效 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

**索引**: `idx_type(type_code)`, `idx_class(class_id)`

---

#### task_assignments (任务分发表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| task_code | VARCHAR(32) | NOT NULL | 任务编码 |
| class_room_code | VARCHAR(20) | - | 班级代码 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| due_date | DATE | NULL | 截止日期 |

**索引**: `idx_classroom(class_room_code, due_date)`

---

#### student_task_assignments (学生任务分发表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| assignment_id | BIGINT | NOT NULL | 父表 task_assignments ID |
| student_id | BIGINT | NOT NULL | 学生 ID |
| status | VARCHAR(20) | DEFAULT 'PENDING' | 状态：PENDING, IN_PROGRESS, COMPLETED, EXPIRED |
| assigned_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 分配时间 |
| completed_at | TIMESTAMP | NULL | 完成时间 |

**索引**: `idx_student_status(student_id, status)`

---

#### assessment_sessions (测评会话表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| session_id | CHAR(36) | UNIQUE NOT NULL | UUID |
| task_code | VARCHAR(32) | NOT NULL | 任务编码 |
| student_id | BIGINT | NOT NULL | 学生 ID |
| start_time | DATETIME | NOT NULL | 开始时间 |
| end_time | DATETIME | NULL | 结束时间 |
| total_time_sec | FLOAT | - | 总耗时(秒) |
| grid_size | TINYINT | - | 网格大小(如 5x5) |
| is_completed | TINYINT | DEFAULT 0 | 是否完成 |

**索引**: `idx_student_task(student_id, task_code)`

---

#### event_summaries (事件汇总表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| session_id | CHAR(36) | NOT NULL | 会话 ID |
| event_type | VARCHAR(20) | - | 事件类型：CLICK, HOVER, COMPLETE |
| grid_cell | TINYINT | - | 点击格子编号 |
| reaction_time_ms | SMALLINT | - | 反应时(毫秒) |
| is_correct | TINYINT | - | 是否正确 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引**: `idx_session(session_id)`

---

#### assessment_results (测评结果表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| user_id | BIGINT | NOT NULL | 用户 ID |
| task_id | BIGINT | - | 任务 ID |
| type_code | VARCHAR(50) | NOT NULL | 测评类型编码 |
| request_id | VARCHAR(100) | - | 请求 ID |
| session_id | VARCHAR(100) | - | 会话 ID |
| score_data | JSON | - | 原始分数 |
| cognitive_profile | JSON | - | 认知画像维度分数 |
| ai_recommendations | JSON | - | AI 建议 |
| report_status | VARCHAR(20) | DEFAULT 'PENDING' | 报告状态：PENDING, PROCESSING, COMPLETED, FAILED |
| status | VARCHAR(20) | DEFAULT 'FINISHED' | 测评状态 |
| started_at | TIMESTAMP | NULL | 开始时间 |
| completed_at | TIMESTAMP | NULL | 完成时间 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引**: `idx_user(user_id)`, `idx_task(task_id)`, `idx_status(report_status)`

---

#### assessment_results_v2 (测评结果表 v2)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| session_id | CHAR(36) | UNIQUE NOT NULL | 会话 ID |
| type_code | VARCHAR(32) | - | 测评类型 |
| target_age_group | VARCHAR(20) | - | 目标年龄组："6-8" |
| avg_reaction_time_ms | SMALLINT | - | 平均反应时 |
| correct_count | TINYINT | - | 正确数 |
| total_clicks | TINYINT | - | 总点击数 |
| validity_status | VARCHAR(20) | - | 有效性：VALID, FLAGGED, INVALID |
| report_generated | TINYINT | DEFAULT 0 | 报告是否已生成 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

---

### 1.3 商城与订单库 (mall_schema)

#### products (商品表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| sku_code | VARCHAR(32) | UNIQUE NOT NULL | SKU 编码 |
| name | VARCHAR(128) | NOT NULL | 商品名称 |
| description | TEXT | - | 商品描述 |
| price_cents | INT | NOT NULL | 价格(分)，¥10.00 → 1000 |
| currency | CHAR(3) | DEFAULT 'CNY' | 货币代码 |
| stripe_price_id | VARCHAR(128) | - | Stripe 商品 ID |
| wechat_pay_product_id | VARCHAR(128) | - | 微信支付产品 ID |
| status | VARCHAR(20) | DEFAULT 'ACTIVE' | 状态 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

---

#### orders (订单表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| order_no | VARCHAR(32) | UNIQUE NOT NULL | 全局订单号 |
| user_id | BIGINT | NOT NULL | 用户 ID |
| student_id | BIGINT | - | 学生 ID（家长购买时） |
| product_sku | VARCHAR(32) | NOT NULL | 商品 SKU |
| amount_cents | INT | NOT NULL | 金额(分) |
| status | VARCHAR(20) | DEFAULT 'PENDING_PAYMENT' | 状态：PENDING, PAID, COMPLETED, REFUNDED, CANCELLED |
| payment_channel | VARCHAR(20) | - | 支付渠道：STRIPE, WECHAT, ALIPAY |
| payment_intent_id | VARCHAR(128) | - | 支付流水号 |
| paid_at | TIMESTAMP | NULL | 支付时间 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

---

#### subscription_plans (订阅方案表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| plan_type | VARCHAR(32) | NOT NULL | 方案类型：MONTHLY, QUARTERLY, YEARLY |
| price_cents | INT | NOT NULL | 价格(分) |
| stripe_price_id | VARCHAR(128) | - | Stripe 价格 ID |
| status | TINYINT | DEFAULT 1 | 状态 |
| expires_at_offset_days | INT | - | 自动续期天数偏移 |

---

### 1.4 AI 服务库 (ai_schema)

#### knowledge_base (知识库表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| doc_id | VARCHAR(64) | UNIQUE NOT NULL | 文档 ID（映射到 Milvus） |
| doc_title | VARCHAR(200) | - | 文档标题 |
| category | VARCHAR(50) | - | 分类 |
| tags | VARCHAR(128)[] | - | 标签数组 |
| embedding_dim | TINYINT | DEFAULT 1536 | 向量维度 |
| version | INT | DEFAULT 1 | 版本号 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

---

#### reports (报告表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| result_id | BIGINT | NOT NULL | 关联 assessment_results |
| user_id | BIGINT | NOT NULL | 查看报告用户 ID |
| report_type | VARCHAR(32) | - | 类型：INDIVIDUAL, CLASS_OVERVIEW, DEVELOPMENT |
| report_json | LONGTEXT | - | 完整 JSON 报告 |
| version | INT | DEFAULT 1 | 版本号 |
| is_official | TINYINT | DEFAULT 0 | 是否官方已签署 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引**: `idx_result(result_id)`

---

## 2. ClickHouse 分析型数据库

### 2.1 assessment_event_records (用户原始测评事件表)

| 字段 | 类型 | 说明 |
|------|------|------|
| event_id | String | 事件 ID |
| user_id | Int64 | 用户 ID |
| session_id | String | 会话 ID |
| task_id | String | 任务 ID |
| type_code | LowCardinality(String) | 测评类型编码 |
| event_type | LowCardinality(String) | 事件类型：CLICK, HOVER, NAVIGATE |
| grid_cell | UInt8 | 点击的格子编号 (1-25 for 5x5) |
| performance_now | Decimal64(6) | 微秒级精度时间 |
| reaction_time_ms | UInt16 | 反应时 (0-65535 ms) |
| pointer_x | Float32 | X 坐标 |
| pointer_y | Float32 | Y 坐标 |
| correct | UInt8 | 正确性 0/1 |
| created_at | DateTime | 创建时间 |
| request_id | String | 请求 ID |

**引擎**: `MergeTree()`
**排序键**: `(user_id, created_at)`
**索引**: `idx_user_time(user_id, created_at) TYPE minmax GRANULARITY 4`

---

### 2.2 assessment_results_agg (用户测评结果聚合表)

| 字段 | 类型 | 说明 |
|------|------|------|
| result_id | String | 结果 ID |
| user_id | Int64 | 用户 ID |
| session_id | String | 会话 ID |
| task_id | String | 任务 ID |
| type_code | LowCardinality(String) | 测评类型编码 |
| total_clicks | UInt32 | 总点击数 |
| correct_clicks | UInt32 | 正确点击数 |
| avg_reaction_time_ms | UInt16 | 平均反应时 |
| min_reaction_time_ms | UInt16 | 最小反应时 |
| p50_reaction_time_ms | UInt16 | 中位反应时 |
| p95_reaction_time_ms | UInt16 | 95 分位反应时 |
| sd_reaction_time_ms | Float32 | 反应时标准差 |
| total_path_length | Float32 | 总路径长度 |
| avg_path_angle | Float32 | 平均路径角度 |
| grid_size | UInt8 | 网格大小 |
| total_time_sec | Float32 | 总耗时(秒) |
| score_value | Float32 | 原始分数 |
| is_flagged | UInt8 | DEFAULT 0，是否被标记 |
| flag_type | LowCardinality(String) | 标记类型 |
| validity_status | LowCardinality(String) | 有效性：VALID, FLAGGED, INVALID |
| started_at | DateTime | 开始时间 |
| completed_at | DateTime | 完成时间 |
| created_at | DateTime | 创建时间 |

**引擎**: `MergeTree()`
**排序键**: `(user_id, started_at)`

---

### 2.3 cognitive_normalize (教育常模表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UInt64 | 主键 |
| age_group | LowCardinality(String) | 年龄组："6-8", "9-11", "12-14", "15-17" |
| dimension | LowCardinality(String) | 认知维度：VISUAL_ATTENTION, WORKING_MEMORY, LOGIC |
| score_mean | Float32 | 均值 |
| score_std | Float32 | 标准差 |
| p25 | Float32 | 25 分位数 |
| p50 | Float32 | 50 分位数 (中位数) |
| p75 | Float32 | 75 分位数 |
| p95 | Float32 | 95 分位数 |
| n | UInt32 | 样本量 |
| updated_at | DateTime | 更新时间 |

**引擎**: `MergeTree()`
**排序键**: `(dimension, age_group)`
**索引**: `idx_age_dim(age_group, dimension) TYPE bm25 GRANULARITY 1`

---

### 2.4 education_knowledge (教育知识表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UInt64 | 主键 |
| category | LowCardinality(String) | 类别：注意力训练、记忆提升、逻辑推理 |
| title | String | 标题 |
| content | String | 内容 |
| source | String | 来源：学术文献/教育专家 |
| tags | Array(String) | 标签数组 |
| embedding_version | Int32 | 对应向量版本 |
| version | Int32 | 版本号 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

**引擎**: `MergeTree()`
**排序键**: `(category, created_at)`
**索引**: `idx_category(category) TYPE tokenbf_v255 GRANULARITY 1`, `idx_tags(tags) TYPE bloom_filter GRANULARITY 1`

---

### 2.5 normalize_version (常模版本管理表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UInt64 | 主键 |
| version | String | 版本号 |
| effective_date | Date | 生效日期 |
| created_at | DateTime | 创建时间 |
| created_by | String | 创建人 |
| change_log | String | JSON 变更日志 |

**引擎**: `MergeTree()`
**排序键**: `id`

---

## 3. MongoDB 文档数据库

### 3.1 event_records (事件记录集合)

```javascript
{
    _id: ObjectId,
    event_id: "event-xxxxx",                    // 事件 ID
    user_id: NumberLong(12345),                 // 用户 ID
    session_id: "session-yyyyy",               // 会话 ID
    type_code: "VISUAL_ATTENTION",             // 测评类型编码
    event_type: "CLICK | HOVER | KEY_DOWN | ASSESSMENT_START",  // 事件类型
    task_id: "task-zzzzz",                     // 任务 ID
    performance_now: 1234567.890123,           // performance.now() 精确值(毫秒)
    reaction_time_ms: NumberInt(420),          // 反应时
    pointer_x: 450,                            // X 坐标
    pointer_y: 320,                            // Y 坐标
    pointer_pressure: 1.0,                     // 触控压力(移动端)
    device_info: {                             // 设备信息
        screen_width: NumberInt(1920),
        screen_height: NumberInt(1080),
        pixel_ratio: 2.0,
        device_pixel_ratio: 2.0,
        browser: "Chrome 120",
        os: "Windows 11",
        dpi: 96
    },
    metadata: {},                              // 元数据
    created_at: ISODate("2026-05-19T08:30:00Z") // 创建时间
}
```

**索引**:
| 索引名 | 字段 | 类型 | 说明 |
|--------|------|------|------|
| 复合索引 | `{user_id: 1, session_id: 1}` | 升序 | 用户会话查询 |
| 时间索引 | `{created_at: -1}` | 降序 | 时间序列查询 |
| 用户时间索引 | `{user_id: 1, created_at: -1}` | 组合 | 用户时间线 |
| TTL 索引 | `{created_at: 1}` | 30天过期 | 自动清理过期数据 |

---

## 4. Redis 缓存

### 4.1 Key 设计规范

| Key 模式 | 数据类型 | 说明 | TTL |
|----------|----------|------|-----|
| `jwt:whitelist:<jti>` | String (1) | 有效 JWT 令牌 | Token 剩余有效期 |
| `jwt:blacklist:<jti>` | String (1) | 吊销 JWT 令牌 | Token 剩余有效期 |
| `session:user:<user_id>` | JSON | 用户会话信息 | 30 天 |
| `rate_limit:gateway:<ip>` | Counter | IP 限流计数器 | 60 秒 |
| `rate_limit:gateway:<api_path>:<user_id>` | Counter | API 限流计数器 | 60 秒 |
| `report:pending:<user_id>:<type_code>` | String (1) | 待处理报告防重 | 5 分钟 |
| `assessment:lock:<session_id>` | JSON | 评测会话锁 | 15 分钟 |

### 4.2 限流配置

| 限流键 | 阈值 | 时间窗口 |
|--------|------|----------|
| IP 级别 | 500 QPS | 60 秒 |
| API 级别 | 100 QPS | 60 秒 |

### 4.3 数据结构使用建议

| 场景 | 数据结构 | 示例 |
|------|----------|------|
| 排行榜/频次 | Sorted Set | 测评历史排名 |
| 计数器 | String / Hash | 用户操作计数 |
| 短期缓存 | String (JSON) | 热点用户信息 |
| 布隆过滤器 | Bloom Filter | 去重判断 |

---

## 5. Milvus 向量数据库

### 5.1 brainspark_knowledge Collection Schema

| 字段 | 类型 | 最大长度 | 说明 |
|------|------|----------|------|
| id | VARCHAR | 64 | 主键，文档 ID |
| doc_title | VARCHAR | 200 | 文档标题 |
| doc_content_short | VARCHAR | 4096 | 简短摘要 |
| doc_content_full | VARCHAR | 65535 | 完整文本 |
| category | VARCHAR | 50 | 分类 |
| tags | ARRAY(VARCHAR) | 容量 20 | 标签数组 |
| embedding | FLOAT_VECTOR | 1536 | 向量嵌入 |
| version | INT32 | - | 版本号 |
| created_at | INT64 | - | 创建时间戳 |

### 5.2 索引配置

| 字段 | 索引类型 | 度量类型 | 参数 |
|------|----------|----------|------|
| embedding | HNSW | IP (内积) | M=16, efConstruction=256 |
| category | INVERTED | - | - |

### 5.3 搜索配置

| 参数 | 值 | 说明 |
|------|-----|------|
| 度量类型 | IP | 内积相似度 |
| ef | 128 | 搜索时枚举数 |
| Top-K | 5 | 默认返回结果数 |

---

## 附录：数据存储流向图

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   MySQL (事务)  │     │   ClickHouse     │     │    MongoDB      │
│                 │     │   (分析)          │     │   (事件原始)    │
│ - 用户数据       │◄────│ - 聚合结果       │     │ - 事件记录      │
│ - 测评任务       │ 写 │ - 常模对比       │     │ - 设备信息      │
│ - 订单订阅       │◄────│ - 知识检索       │     │                 │
│ - 报告存储       │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                         │                        │
        ▼                         ▼                        ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│    Redis        │     │   Milvus         │     │  数据流向       │
│   (缓存/锁)     │     │  (向量检索)       │     │                 │
│                 │     │                  │     │ Flink/ETL       │
│ - JWT Token     │     │ - 教育知识嵌入    │     │ 事件 → MongoDB   │
│ - 会话缓存      │     │ - RAG 检索       │     │ 聚合 → ClickHouse│
│ - 限流计数器    │     │                  │     │ 结果 → MySQL    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

> **文档维护指南**: 
> 1. 新增表请在此文档添加对应章节
> 2. 修改 DDL 请同步更新所有源文档
> 3. 表结构变更需记录修改日志
> 4. 保持所有数据模型与 [`docs/optimization-plan.md`](../optimization-plan.md) 中定义的分层架构一致