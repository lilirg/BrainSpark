# BrainSpark 后端业务服务设计文档

> 本文档详细描述 BrainSpark 平台后端业务服务 (`backend-business`) 的架构与设计。该服务采用 Spring Boot 3 实现，负责核心业务逻辑处理。

## 1. 架构概述

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Gateway Layer                                │
│  ┌─────────────────────┐    ┌───────────────────────────────────┐   │
│  │  Go API Gateway     │    │  Go WebSocket Gateway             │   │
│  │  (port 8081)         │    │  (port 8082)                      │   │
│  └─────────────────────┘    └───────────────────────────────────┘   │
└───────────────┬──────────────────────────────┬──────────────────────┘
                │                              │
                ▼                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Service Layer                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Java Backend (Spring Boot 3)                                   │  │
│  │  (port 8080)                                                    │  │
│  │                                                               │  │
│  │  ┌───────────────────────────────────────────────────────┐    │  │
│  │  │  Controller Layer                                       │    │  │
│  │  │  - 用户管理   - 班级管理  - 测评任务   - 报告服务      │    │  │
│  │  │  - 订单支付   - 内容管理  - 运营管理   - 通知推送      │    │  │
│  │  └───────────────────────────────────────────────────────┘    │  │
│  │                                                               │  │
│  │  ┌───────────────────────────────────────────────────────┐    │  │
│  │  │  Service Layer                                        │    │  │
│  │  │  - 用户服务   - 测评服务  - AI 服务接口  - 订单服务    │    │  │
│  │  │  - 报告服务   - 内容服务  - 通知服务                   │    │  │
│  │  └───────────────────────────────────────────────────────┘    │  │
│  │                                                               │  │
│  │  ┌───────────────────────────────────────────────────────┐    │  │
│  │  │  Repository Layer                                     │    │  │
│  │  │  - MySQL (JPA)   - MongoDB (Spring Data)              │    │  │
│  │  └───────────────────────────────────────────────────────┘    │  │
│  │                                                               │  │
│  │  ┌───────────────────────────────────────────────────────┐    │  │
│  │  │  Async Layer                                          │    │  │
│  │  │  - Kafka Producer   - Redis Cache                     │    │  │
│  │  │  - ClickHouse Batch Write                             │    │  │
│  │  └───────────────────────────────────────────────────────┘    │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                            │           │
                            ▼           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Data Layer                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  MySQL   │  │ MongoDB  │  │ Redis    │  │ ClickHouse│           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. 目录结构

```
apps/backend-business/
├── pom.xml                                    # Maven 配置
├── docker/
│   └── Dockerfile
├── src/
│   ├── main/
│   │   ├── java/com/brainspark/
│   │   │   ├── BrainSparkApplication.java     # 启动类
│   │   │   ├── config/                        # 配置类
│   │   │   │   ├── SecurityConfig.java        # Spring Security 配置
│   │   │   │   ├── JwtAuthenticationFilter.java # JWT 过滤器
│   │   │   │   ├── RedisConfig.java           # Redis 配置
│   │   │   │   ├── MongoConfig.java           # MongoDB 配置
│   │   │   │   ├── KafkaConfig.java           # Kafka 配置
│   │   │   │   ├── ClickHouseConfig.java      # ClickHouse 配置 (JDBC)
│   │   │   │   ├── OpenApiConfig.java         # Swagger/OpenAPI 配置
│   │   │   │   └── AsyncConfig.java           # 异步线程池配置
│   │   │   ├── controller/                    # 控制器
│   │   │   │   ├── AuthController.java        # 认证接口 (登录/注册/刷新)
│   │   │   │   ├── UserController.java        # 用户管理 (CRUD)
│   │   │   │   ├── ClassController.java       # 班级管理
│   │   │   │   ├── AssessmentTaskController.java # 测评任务管理
│   │   │   │   ├── AssessmentResultsController.java # 测评结果
│   │   │   │   ├── ReportController.java      # 报告服务
│   │   │   │   ├── OrderController.java       # 订单管理
│   │   │   │   ├── PaymentController.java     # 支付接口
│   │   │   │   ├── SubscriptionController.java # 订阅管理
│   │   │   │   ├── ContentController.java     # 内容管理 (测评/题库)
│   │   │   │   ├── KnowledgeBaseController.java # 知识库管理
│   │   │   │   ├── NotificationController.java # 通知推送
│   │   │   │   ├── OperationStatsController.java # 运营统计
│   │   │   │   ├── OrganizationController.java # 机构管理
│   │   │   │   └── HealthController.java      # 健康检查
│   │   │   ├── service/                       # 业务逻辑
│   │   │   │   ├── UserService.java           # 用户服务
│   │   │   │   ├── AuthService.java           # 认证服务
│   │   │   │   ├── JwtService.java            # JWT 服务
│   │   │   │   ├── ClassService.java          # 班级服务
│   │   │   │   ├── AssessmentTaskService.java # 测评任务服务
│   │   │   │   ├── AssessmentService.java     # 测评服务
│   │   │   │   ├── ReportService.java         # 报告服务
│   │   │   │   ├── AiServiceClient.java       # AI 服务客户端
│   │   │   │   ├── OrderService.java          # 订单服务
│   │   │   │   ├── PaymentService.java        # 支付服务
│   │   │   │   ├── SubscriptionService.java   # 订阅服务
│   │   │   │   ├── ContentService.java        # 内容服务
│   │   │   │   ├── NotificationService.java   # 通知服务
│   │   │   │   ├── EventProcessingService.java # 事件处理服务
│   │   │   │   └── ComplianceService.java     # 合规服务 (脱敏/加密)
│   │   │   ├── repository/                    # 数据访问层
│   │   │   │   ├── UserRepository.java        # 用户 (MySQL)
│   │   │   │   ├── ClassRepository.java       # 班级 (MySQL)
│   │   │   │   ├── AssessmentTaskRepository.java # 测评任务 (MySQL)
│   │   │   │   ├── OrderRepository.java       # 订单 (MySQL)
│   │   │   │   ├── SubscriptionRepository.java # 订阅 (MySQL)
│   │   │   │   ├── EventRecordRepository.java  # 事件记录 (MongoDB)
│   │   │   │   └── NotificationRepository.java # 通知 (MySQL)
│   │   │   ├── entity/                        # 实体类
│   │   │   │   ├── User.java                  # 用户实体
│   │   │   │   ├── Class.java                 # 班级实体
│   │   │   │   ├── AssessmentTask.java        # 测评任务实体
│   │   │   │   ├── AssessmentResult.java      # 测评结果实体
│   │   │   │   ├── Order.java                 # 订单实体
│   │   │   │   ├── Subscription.java          # 订阅实体
│   │   │   │   ├── ContentItem.java           # 内容条目实体
│   │   │   │   ├── KnowledgeBase.java         # 知识库实体
│   │   │   │   ├── Notification.java          # 通知实体
│   │   │   │   ├── Organization.java          # 机构实体
│   │   │   │   └── EventRecord.java           # 事件记录 (MongoDB)
│   │   │   ├── dto/                           # 数据传输对象
│   │   │   │   ├── auth/                      # 认证相关
│   │   │   │   │   ├── LoginRequest.java
│   │   │   │   │   ├── LoginResponse.java
│   │   │   │   │   └── RefreshTokenRequest.java
│   │   │   │   ├── user/                      # 用户相关
│   │   │   │   │   ├── UserCreateRequest.java
│   │   │   │   │   ├── UserUpdateRequest.java
│   │   │   │   │   └── UserProfileResponse.java
│   │   │   │   ├── assessment/                # 测评相关
│   │   │   │   │   ├── AssessmentTaskRequest.java
│   │   │   │   │   ├── AssessmentResultResponse.java
│   │   │   │   │   └── CognitiveProfile.java
│   │   │   │   ├── report/                    # 报告相关
│   │   │   │   │   ├── ReportGenerateRequest.java
│   │   │   │   │   └── ReportResponse.java
│   │   │   │   ├── order/                     # 订单相关
│   │   │   │   │   ├── OrderCreateRequest.java
│   │   │   │   │   ├── OrderResponse.java
│   │   │   │   │   └── PaymentCallback.java
│   │   │   │   ├── notification/              # 通知相关
│   │   │   │   │   ├── NotificationCreateRequest.java
│   │   │   │   │   └── NotificationResponse.java
│   │   │   │   └── common/                    # 通用
│   │   │   │       ├── PageResponse.java
│   │   │   │       └── ApiResponse.java
│   │   │   ├── enums/                         # 枚举定义
│   │   │   │   ├── UserRole.java              # 用户角色
│   │   │   │   ├── OrderStatus.java           # 订单状态
│   │   │   │   ├── PaymentMethod.java         # 支付方式
│   │   │   │   ├── SubscriptionPlan.java      # 订阅方案
│   │   │   │   ├── AssessmentType.java        # 测评类型
│   │   │   │   └── NotificationType.java      # 通知类型
│   │   │   ├── exception/                     # 异常处理
│   │   │   │   ├── BusinessException.java     # 业务异常
│   │   │   │   ├── ResourceNotFoundException.java # 资源未找到
│   │   │   │   ├── DuplicateResourceException.java # 重复资源
│   │   │   │   └── GlobalExceptionHandler.java # 全局异常处理器
│   │   │   └── util/                          # 工具类
│   │   │       ├── EncryptionUtils.java       # 加密工具
│   │   │       ├── ComplianceUtils.java       # 合规脱敏工具
│   │   │       └── DateUtils.java             # 日期工具
│   │   └── resources/
│   │       ├── application.yml                # 主配置文件
│   │       ├── application-dev.yml            # 开发环境配置
│   │       ├── application-prod.yml           # 生产环境配置
│   │       └── db/migration/                  # Flyway 数据库迁移脚本
│   │           ├── V1__init_schema.sql
│   │           ├── V2__add_assessment_tables.sql
│   │           └── V3__add_order_tables.sql
│   └── test/
│       └── java/com/brainspark/
│           ├── controller/
│           ├── service/
│           └── repository/
└── README.md
```

## 3. 数据库设计

### 3.1 核心实体关系

```mermaid
erDiagram
    organization ||--o{ class : owns
    class ||--o{ user : has
    user ||--o{ student-profile : contains
    user ||--o{ assessment-task : creates
    user ||--o{ subscription : has
    user ||--o{ order : places
    class ||--o{ student-profile : has
    user ||--o{ assessment-result : completes
    assessment-task ||--o{ assessment-result : generates
    assessment-result }o--|| assessment-type : belongs
    assessment-result ||--|| report : generates
    user ||--o{ content-item : manages
    user ||--o{ notification : receives
    assessment-type }o--|| cognitive-dimension : belongs
    order ||--|| subscription : enables

    organization {
        bigint id PK
        string name
        string contact
        string status
    }

    class {
        bigint id PK
        bigint org_id FK
        string name
        string grade
        string teacher_id FK
        datetime created_at
    }

    user {
        bigint id PK
        string username
        string password_hash
        enum role
        string real_name
        string avatar
        json extra_info
        datetime created_at
        datetime updated_at
    }

    student-profile {
        bigint id PK
        bigint user_id FK
        date birth_date
        string school
        string grade
        json health_info
        boolean has_guardian_consent
        datetime consent_time
    }

    assessment-task {
        bigint id PK
        bigint org_id FK
        string title
        string type
        json config
        int difficulty
        int duration_min
        boolean is_active
        datetime created_at
    }

    assessment-result {
        bigint id PK
        bigint user_id FK
        bigint task_id FK
        string request_id
        json score_data
        json cognitive_profile
        string status
        datetime started_at
        datetime completed_at
        datetime created_at
    }

    order {
        bigint id PK
        bigint user_id FK
        string order_no
        enum status
        bigint amount_cents
        enum payment_method
        string payment_url
        json callback_data
        datetime created_at
        datetime paid_at
    }

    subscription {
        bigint id PK
        bigint user_id FK
        enum plan
        datetime start_time
        datetime end_time
        boolean is_active
        string payment_id FK
    }
```

### 3.2 MySQL 核心表

```sql
-- 用户表
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL, -- ADMIN, TEACHER, STUDENT, PARENT, OPERATOR
    real_name VARCHAR(50),
    avatar VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(100),
    status VARCHAR(20) DEFAULT 'ACTIVE', -- ACTIVE, DISABLED, PENDING_VERIFY
    extra_info JSON, -- 额外属性（年龄、年级等）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_role (role),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 家长学生关联表
CREATE TABLE family_bindings (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    parent_user_id BIGINT NOT NULL,
    student_user_id BIGINT NOT NULL,
    binding_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_parent (parent_user_id),
    INDEX idx_student (student_user_id),
    UNIQUE KEY uk_family (parent_user_id, student_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 班级表
CREATE TABLE classes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    org_id BIGINT,
    name VARCHAR(100) NOT NULL,
    grade VARCHAR(20),
    description TEXT,
    teacher_id BIGINT,
    max_students INT DEFAULT 50,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 班级成员表
CREATE TABLE class_members (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    class_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    role VARCHAR(20), -- STUDENT, TEACHER
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_class_member (class_id, user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 测评类型表
CREATE TABLE assessment_types (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE, -- SCHULTER, DIGITAL_SPAN, PATTERN_REASONING
    name VARCHAR(100) NOT NULL,
    description TEXT,
    cognitive_dimension VARCHAR(50), -- VISUAL, AUDITORY, MEMORY, LOGIC
    duration_seconds INT,
    version VARCHAR(20),
    config JSON, -- 测评参数
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 测评任务表
CREATE TABLE assessment_tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    org_id BIGINT,
    class_id BIGINT,
    title VARCHAR(200) NOT NULL,
    type_code VARCHAR(50) NOT NULL,
    config JSON, -- 任务配置（难度、顺序、白/黑卡）
    difficulty INT DEFAULT 1,
    duration_min INT DEFAULT 10,
    assigned_at TIMESTAMP,
    start_at TIMESTAMP,
    end_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_type (type_code),
    INDEX idx_class (class_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 测评结果表
CREATE TABLE assessment_results (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    task_id BIGINT,
    type_code VARCHAR(50) NOT NULL,
    request_id VARCHAR(100),
    session_id VARCHAR(100),
    score_data JSON, -- 原始分数
    cognitive_profile JSON, -- 认知画像维度分数
    ai_recommendations JSON, -- AI 建议
    report_status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, PROCESSING, COMPLETED, FAILED
    status VARCHAR(20) DEFAULT 'FINISHED',
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_task (task_id),
    INDEX idx_status (report_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 3.3 MongoDB 集合设计

```javascript
// 事件记录集合 (事件记录)
{
    _id: ObjectId,
    event_id: "event-xxxxx",
    user_id: 12345,
    session_id: "session-yyyyy",
    type: "CLICK | HOVER | KEY_DOWN | ASSESSMENT_START | ASSESSMENT_COMPLETE",
    task_id: "task-zzzzz",
    performance_start: 1234567.890123,  // performance.now() 精确值 (毫秒)
    pointer_x: 450,
    pointer_y: 320,
    pointer_pressure: 1.0,
    device_info: {
        screen_width: 1920,
        screen_height: 1080,
        pixel_ratio: 2.0,
        device_pixel_ratio: 2.0,
        browser: "Chrome 120",
        os: "Windows 11",
        dpi: 96
    },
    metadata: {},
    created_at: ISODate("2026-05-19T08:30:00Z")
}

// 索引
db.event_records.createIndex({ user_id: 1, session_id: 1 })
db.event_records.createIndex({ created_at: -1 })
db.event_records.createIndex({ user_id: 1, created_at: -1 })
```

### 3.4 ClickHouse 表设计

```sql
CREATE TABLE event_records_ch (
    event_id String,
    user_id Int64,
    session_id String,
    type LowCardinality(String),
    task_id String,
    performance_start Decimal64(6),  -- 微秒级精度
    pointer_x Float32,
    pointer_y Float32,
    created_at DateTime,
    request_id String
) ENGINE = MergeTree()
ORDER BY (user_id, created_at)
SETTINGS index_granularity = 8192;

CREATE TABLE assessment_results_ch (
    user_id Int64,
    task_id String,
    type_code LowCardinality(String),
    score_value Float64,
    score_percentile Float64,
    age_group String,  -- 年龄分组常模对比
    created_at DateTime,
    request_id String
) ENGINE = MergeTree()
ORDER BY (user_id, created_at);
```

## 4. API 接口设计

### 4.1 认证接口

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/v1/auth/login` | 登录 (获取 JWT) | 无 |
| `POST` | `/api/v1/auth/refresh` | 刷新 token | Bearer Token |
| `POST` | `/api/v1/auth/logout` | 登出 | Bearer Token |
| `POST` | `/api/v1/auth/register` | 注册 (家长/教师) | 无 |

```json
// POST /api/v1/auth/login 请求
{
    "username": "teacher01",
    "password": "secure-password"
}

// 响应
{
    "code": 200,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "Bearer",
        "expires_in": 3600,
        "user": {
            "id": 12345,
            "username": "teacher01",
            "role": "TEACHER",
            "real_name": "张老师"
        }
    }
}
```

### 4.2 用户管理接口

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/users/me` | 获取当前用户信息 | Bearer Token |
| `PUT` | `/api/v1/users/me` | 更新当前用户信息 | Bearer Token |
| `GET` | `/api/v1/users/{id}` | 获取用户详情 | Bearer Token |
| `GET` | `/api/v1/users` | 用户列表 (分页) | Bearer Token |
| `POST` | `/api/v1/users` | 创建用户 (家长/教师) | Bearer Token (Manager/Admin) |
| `DELETE` | `/api/v1/users/{id}` | 注销用户 | Bearer Token (Admin) |

### 4.3 班级管理接口

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/classes` | 班级列表 (分页) | Bearer Token |
| `POST` | `/api/v1/classes` | 创建班级 | Bearer Token (Teacher/Manager) |
| `GET` | `/api/v1/classes/{id}` | 班级详情 | Bearer Token |
| `PUT` | `/api/v1/classes/{id}` | 更新班级 | Bearer Token (Teacher/Manager) |
| `GET` | `/api/v1/classes/{id}/members` | 班级成员列表 | Bearer Token |
| `POST` | `/api/v1/classes/{id}/members` | 添加成员 | Bearer Token (Teacher/Manager) |
| `DELETE` | `/api/v1/classes/{id}/members/{user_id}` | 移除成员 | Bearer Token (Teacher/Manager) |

### 4.4 测评接口

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/assessment/tasks` | 获取测评任务列表 | Bearer Token |
| `POST` | `/api/v1/assessment/tasks` | 创建测评任务 | Bearer Token (Teacher/Manager) |
| `GET` | `/api/v1/assessment/tasks/{id}` | 获取任务详情 | Bearer Token |
| `DELETE` | `/api/v1/assessment/tasks/{id}` | 删除测评任务 | Bearer Token (Manager) |
| `GET` | `/api/v1/assessment/results` | 获取测评结果列表 | Bearer Token |
| `GET` | `/api/v1/assessment/results/{id}` | 获取测评详情 | Bearer Token |
| `GET` | `/api/v1/assessment/available` | 获取可测试任务 | Bearer Token (Student) |

### 4.5 报告接口

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/reports` | 获取报告列表 | Bearer Token |
| `POST` | `/api/v1/reports/generate` | 生成 AI 报告 | Bearer Token (Teacher/Manager) |
| `GET` | `/api/v1/reports/{id}` | 获取报告详情 | Bearer Token |
| `POST` | `/api/v1/reports/{id}/feedback` | 提交反馈 | Bearer Token (Teacher) |

```json
// POST /api/v1/reports/generate 请求
{
    "user_id": 12345,
    "assessment_result_ids": [1, 2, 3],
    "include_recommendations": true,
    "include_trend_analysis": true
}
```

### 4.6 订单支付接口

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/orders` | 订单列表 (分页) | Bearer Token |
| `POST` | `/api/v1/orders` | 创建订单 | Bearer Token |
| `GET` | `/api/v1/orders/{order_no}` | 订单详情 | Bearer Token |
| `POST` | `/api/v1/payments/create` | 创建支付 | Bearer Token |
| `POST` | `/api/v1/payments/callback/wechat` | 微信支付回调 | 签名验证 |
| `POST` | `/api/v1/payments/callback/alipay` | 支付宝回调 | 签名验证 |

### 4.7 订阅管理接口

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/subscriptions` | 订阅详情 | Bearer Token |
| `POST` | `/api/v1/subscriptions/renew` | 续费订阅 | Bearer Token |
| `POST` | `/api/v1/subscriptions/cancel` | 取消订阅 | Bearer Token |
| `POST` | `/api/v1/subscriptions/reactivate` | 重新激活 | Bearer Token |

### 4.8 运营接口

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/stats/dashboard` | 仪表盘统计 | Bearer Token (Admin) |
| `GET` | `/api/v1/stats/users` | 用户统计 | Bearer Token (Admin) |
| `GET` | `/api/v1/stats/assessments` | 测评统计 | Bearer Token (Manager/Admin) |
| `GET` | `/api/v1/stats/financial` | 财务统计 | Bearer Token (Admin) |

### 4.9 统一响应格式

```json
{
    "code": 200,
    "message": "ok",
    "data": {
        // 业务数据
    },
    "request_id": "bs-1234567890-abc12345"
}

// 错误响应
{
    "code": 400,
    "message": "参数校验失败",
    "data": null,
    "errors": [
        {
            "field": "email",
            "message": "邮箱格式不正确"
        }
    ],
    "request_id": "bs-1234567890-abc12345"
}
```

### 4.10 分页响应格式

```json
{
    "code": 200,
    "data": {
        "items": [],
        "total": 100,
        "page": 1,
        "size": 20,
        "total_pages": 5
    }
}
```

## 5. 核心业务逻辑

### 5.1 用户认证服务

```java
// service/AuthService.java
@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;

    public LoginResponse login(LoginRequest request) {
        User user = userRepository.findByUsername(request.username())
            .orElseThrow(() -> new BusinessException("Invalid credentials"));

        if (!passwordEncoder.matches(request.password(), user.getPasswordHash())) {
            throw new BusinessException("Invalid credentials");
        }

        String accessToken = jwtService.generateAccessToken(user);
        String refreshToken = jwtService.generateRefreshToken(user);

        return new LoginResponse(accessToken, refreshToken, user.toDto());
    }

    public void register(RegisterRequest request) {
        if (userRepository.findByUsername(request.username()).isPresent()) {
            throw new DuplicateResourceException("User already exists");
        }

        User user = new User();
        user.setUsername(request.username());
        user.setPasswordHash(passwordEncoder.encode(request.password()));
        user.setRole(request.role());
        user.setRealName(request.realName());
        user.setStatus("PENDING_VERIFY");

        // 未成年模式：注册后需要家长同意
        if (user.getRole() == UserRole.STUDENT) {
            user.setExtraInfo(Map.of("needs_consent", true));
        }

        userRepository.save(user);
    }
}
```

### 5.2 JWT 认证过滤器

```java
// config/JwtAuthenticationFilter.java
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final UserRepository userRepository;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {
        
        final String authHeader = request.getHeader("Authorization");
        
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        final String jwt = authHeader.substring(7);
        final String username = jwtService.extractUsername(jwt);

        if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            User user = userRepository.findByUsername(username).orElse(null);

            if (jwtService.isTokenValid(jwt, user)) {
                UsernamePasswordAuthenticationToken authToken = 
                    new UsernamePasswordAuthenticationToken(
                        user, null, user.getAuthorities());
                SecurityContextHolder.getContext().setAuthentication(authToken);
            }
        }

        filterChain.doFilter(request, response);
    }
}
```

### 5.3 测评结果处理流程

```
用户完成测评 
  │
  ▼
学生端发送事件数据到 Go 网关
  │
  ▼
Go 网关批量写入 MongoDB/Redis
  │
  ▼
Kafka 事件 -> Java 后端消费
  │
  ▼
事件聚合 & 有效性校验 (防作弊)
  │
  ▼
计算认知维度分数
  │
  ▼
写入 MySQL (assessment_results)
  │
  ▼
触发异步报告生成 (通过 Kafka -> AI 服务)
  │
  ▼
AI 服务生成报告 -> 回调 Java 后端
  │
  ▼
更新报告状态
```

```java
// controller/AssessmentResultsController.java
@RestController
@RequestMapping("/api/v1/assessment/results")
@RequiredArgsConstructor
public class AssessmentResultsController {

    private final AssessmentService assessmentService;

    @GetMapping
    public ResponseEntity<PageResponse<AssessmentResultResponse>> getResults(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String typeCode,
            Authentication authentication) {
        
        // ... 获取用户 ID
        User user = getCurrentUser(authentication);
        Page<AssessmentResult> results = assessmentService.findResults(userId, typeCode, page, size);
        
        PageResponse<AssessmentResultResponse> response = results.map(AssessmentResultResponse::from);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<AssessmentResultResponse> getResult(
            @PathVariable Long id,
            Authentication authentication) {
        
        // 权限校验：只有本人/班主任/管理员可查看
        if (!hasPermission(authentication, id)) {
            throw new BusinessException("Forbidden");
        }
        
        AssessmentResult result = assessmentService.findById(id);
        return ResponseEntity.ok(AssessmentResultResponse.from(result));
    }
}
```

### 5.4 报告服务 - AI 报告生成

```java
// service/ReportService.java
@Service
@RequiredArgsConstructor
@Slf4j
public class ReportService {

    private final AssessmentResultRepository assessmentResultRepository;
    private final ReportRepository reportRepository;
    private final AiServiceClient aiServiceClient;
    private final KafkaTemplate<String, String> kafkaTemplate;

    @Transactional
    public Report generateReport(String userId, List<Long> resultIds) {
        // 1. 获取测评结果
        List<AssessmentResult> results = assessmentResultRepository.findByIdIn(resultIds);
        
        // 2. 合规校验
        complianceService.validateAccess(userId, results);
        
        // 3. 脱敏处理
        results.forEach(r -> complianceService.sanitizeSensitiveData(r));
        
        // 4. 触发异步报告生成 (发送给 Kafka)
        KafkaReportEvent event = new KafkaReportEvent();
        event.setUserId(userId);
        event.setResultIds(resultIds);
        
        kafkaTemplate.send("report.generation", event);
        
        // 5. 返回报告占位符
        Report report = new Report();
        report.setUserId(userId);
        report.setStatus(ReportStatus.PENDING);
        report.setAiRecommendations(Map.of());
        report = reportRepository.save(report);
        
        return report;
    }

    public void onCompleteReportGeneration(String reportId, String aiContent) {
        Report report = reportRepository.findById(reportId)
            .orElseThrow(() -> new ResourceNotFoundException("Report not found"));
        
        report.setStatus(ReportStatus.COMPLETED);
        report.setAiContent(aiContent);
        report.setGeneratedAt(LocalDateTime.now());
        reportRepository.save(report);
    }
}
```

### 5.5 订单状态机

```java
// enums/OrderStatus.java
public enum OrderStatus {
    CREATED("已创建"),
    PENDING_PAY("待支付"),
    PAID("已支付"),
    COMPLETED("已完成"),
    CANCELLED("已取消"),
    REFUNDED("已退款");

    private final String label;

    OrderStatus(String label) {
        this.label = label;
    }
}

// service/OrderService.java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;
    private final UserRepository userRepository;

    @Transactional
    public Order createOrder(String userId, String planCode, BigDecimal amount) {
        User user = userRepository.findById(Long.parseLong(userId))
            .orElseThrow(() -> new ResourceNotFoundException("User not found"));
        
        // 生成订单号
        String orderNo = "ORD" + System.currentTimeMillis() + UUID.randomUUID().toString().substring(0, 6);
        
        Order order = new Order();
        order.setOrderNo(orderNo);
        order.setUserId(userId);
        order.setStatus(OrderStatus.CREATED);
        order.setAmountCents(amount.multiply(BigDecimal.valueOf(100)).intValue());
        order.setCreatedAt(LocalDateTime.now());
        
        return orderRepository.save(order);
    }

    @Transactional
    public Order handlePayment(String orderNo, PaymentCallback callback) {
        Order order = findByOrderNo(orderNo);
        
        // 验证回调签名
        if (!paymentService.verifyCallback(callback)) {
            throw new BusinessException("Invalid callback signature");
        }
        
        order.setStatus(OrderStatus.PAID);
        order.setPaymentData(callback);
        order.setPaidAt(LocalDateTime.now());
        
        orderRepository.save(order);
        
        // 更新订阅状态
        subscriptionService.activateSubscription(order);
        
        return order;
    }

    @Transactional
    public Order cancelOrder(String orderNo) {
        Order order = findByOrderNo(orderNo);
        
        if (order.getStatus() != OrderStatus.CREATED) {
            throw new BusinessException("Order can only be cancelled when in CREATED status");
        }
        
        order.setStatus(OrderStatus.CANCELLED);
        orderRepository.save(order);
        
        return order;
    }
}
```

## 6. 安全设计

### 6.1 Spring Security 配置

```java
// config/SecurityConfig.java
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthFilter;
    private final UserDetailsService userDetailsService;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigurer::disable)
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/v1/auth/**").permitAll()
                .requestMatchers("/api/v1/health").permitAll()
                .requestMatchers("/api/v1/admin/**").hasRole("ADMIN")
                .requestMatchers("/api/v1/operation/**").hasAnyRole("TEACHER", "MANAGER", "ADMIN")
                .requestMatchers("/api/v1/users/{id}").hasRole("TEACHER")
                .anyRequest().authenticated()
            )
            .sessionManagement(session -> 
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

### 6.2 未成年用户合规脱敏

```java
// util/ComplianceUtils.java
@Component
public class ComplianceUtils {

    public User sanitizeForAi(User user) {
        User sanitized = new User();
        sanitized.setId(user.getId());
        sanitized.setUsername(anonymize(user.getUsername()));  // "user123" -> "U_******"
        sanitized.setRole(user.getRole());
        sanitized.setRealName(anonymize(user.getRealName()));   // "张三" -> "张*"
        sanitized.setExtraInfo(filterSensitiveFields(user.getExtraInfo()));
        sanitized.setPhone(maskPhone(user.getPhone()));         // "13812345678" -> "138****5678"
        return sanitized;
    }

    private String anonymize(String name) {
        if (name == null || name.length() <= 1) return name;
        return name.charAt(0) + "*****";
    }

    private String maskPhone(String phone) {
        if (phone == null) return null;
        return phone.substring(0, 3) + "****" + phone.substring(7);
    }

    private Map<String, Object> filterSensitiveFields(Map<String, Object> extraInfo) {
        // 过滤身份证号、医院信息等敏感字段
        Set<String> filteredKeys = extraInfo.keySet().stream()
            .filter(key -> !SENSITIVE_FIELDS.contains(key))
            .collect(Collectors.toSet());
        
        return filteredKeys.stream()
            .collect(Collectors.toMap(
                key -> key,
                extraInfo::get
            ));
    }
}
```

## 7. 异步处理机制

### 7.1 Kafka 消息主题

| 主题 | 生产者 | 消费者 | 描述 |
|------|--------|--------|------|
| `event.ingestion` | Go 网关 | Java 后端 | 事件数据流入 |
| `event.processing` | Java 后端 | Java 后端 (ClickHouse 写入) | 事件聚合与存储 |
| `report.generation` | Java 后端 | Java 后端 (触发 AI) | 请求 AI 生成报告 |
| `report.complete` | AI 服务 | Java 后端 | 报告生成完成回调 |
| `notification.push` | Java 后端 | 通知服务 | 消息推送 |
| `payment.completed` | 支付网关 | Java 后端 | 支付成功回调 |

### 7.2 异步事件处理

```java
// config/AsyncConfig.java
@Configuration
@EnableAsync
public class AsyncConfig {

    @Bean(name = "eventExecutor")
    public Executor eventExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(20);
        executor.setQueueCapacity(1000);
        executor.setThreadNamePrefix("event-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        return executor;
    }
}

// service/EventProcessingService.java
@Service
@RequiredArgsConstructor
public class EventProcessingService {

    private final EventRepository eventRepository;
    private final KafkaTemplate<String, String> kafkaTemplate;
    private final MongoTemplate mongoTemplate;

    @Async("eventExecutor")
    public void processEventBulk(List<EventRecord> events) {
        for (EventRecord event : events) {
            // 1. 写入 MongoDB
            mongoTemplate.insert(event);
            
            // 2. 发布到 Kafka 供其他服务消费
            String kafkaPayload = serialize(event);
            kafkaTemplate.send("event.ingestion", String.valueOf(event.getUserId()), kafkaPayload);
        }
    }

    @KafkaListener(topics = "assessment.complete", groupId = "event-processor")
    public void onAssessmentCompleted(AssessmentCompletedEvent event) {
        // 触发报告生成
        reportService.generateReport(event.getUserId(), event.getAssessmentTaskId());
    }
}
```

## 8. 配置文件

### 8.1 开发环境 (`application-dev.yml`)

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/brainspark_dev?useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: dev_password
  
  data:
    mongodb:
      uri: mongodb://localhost:27017/brainspark_events
    redis:
      url: redis://localhost:6379

  kafka:
    bootstrap-servers: localhost:9092

  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true

clickhouse:
  jdbc:
    url: jdbc:clickhouse://localhost:8123/brainspark
    username: default
    password:

jwt:
  secret: dev-super-secret-key-change-in-production
  access-expiration: 3600000  # 1 小时
  refresh-expiration: 86400000  # 24 小时

app:
  frontend:
    url: http://localhost:5173
  domain:
    origin: localhost
  
  compliance:
    anonymize-pii: true

logging:
  level:
    com.braSpark: DEBUG
```

### 8.2 生产环境 (`application-prod.yml`)

```yaml
spring:
  datasource:
    url: jdbc:mysql://${MYSQL_HOST}:3306/brainspark_prod?useSSL=true&serverTimezone=Asia/Shanghai
    username: ${MYSQL_USERNAME}
    password: ${MYSQL_PASSWORD}
    hikari:
      maximum-pool-size: 30
      minimum-idle: 5
  
  data:
    mongodb:
      uri: ${MONGODB_URI}
    redis:
      url: ${REDIS_URL}

  kafka:
    bootstrap-servers: ${KAFKA_BOOTSTRAP_SERVERS}

  jpa:
    hibernate:
      ddl-auto: none
    show-sql: false

clickhouse:
  jdbc:
    url: ${CLICKHOUSE_URL}
    username: ${CLICKHOUSE_USERNAME}
    password: ${CLICKHOUSE_PASSWORD}

jwt:
  secret: ${JWT_SECRET}
  access-expiration: 3600000
  refresh-expiration: 86400000

app:
  frontend:
    url: ${FRONTEND_URL}
  domain:
    origin: ${DOMAIN_ORIGIN}
  
  ai:
    endpoint: ${AI_SERVICE_ENDPOINT}
    timeout: 30000

logging:
  level:
    com.braSpark: INFO

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
```

## 9. 部署与运维

### 9.1 Docker 配置

```dockerfile
# docker/Dockerfile
FROM eclipse-temurin:17-jdk-alpine AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN chmod +x mvnw && ./mvnw package -DskipTests

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

COPY --from=builder /app/target/backend-business-0.1.0.jar app.jar

RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  business-backend:
    build: ./apps/backend-business
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - MYSQL_HOST=mysql
      - MONGODB_URI=mongodb://mongo:27017/brainspark_events
      - REDIS_URL=redis://redis:6379
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - CLICKHOUSE_URL=clickhouse://clickhouse:8123/brainspark
    depends_on:
      - mysql
      - mongo
      - redis
      - kafka
      - clickhouse
```

### 9.2 健康检查端点

```java
@RestController
@RequestMapping("/api/v1/health")
public class HealthController {

    @GetMapping
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> details = new LinkedHashMap<>();
        details.put("version", "0.1.0");
        details.put("timestamp", System.currentTimeMillis());

        try {
            details.put("database", "ok");
            // 检查数据库连接
        } catch (Exception e) {
            details.put("database", "error: " + e.getMessage());
        }

        try {
            details.put("redis", "ok");
            // 检查 Redis 连接
        } catch (Exception e) {
            details.put("redis", "error: " + e.getMessage());
        }

        int status = details.values().stream()
            .anyMatch(v -> "error".equals(v)) ? 503 : 200;

        HttpStatus httpStatus = status == 200 
            ? HttpStatus.OK 
            : HttpStatus.SERVICE_UNAVAILABLE;

        return ResponseEntity.status(httpStatus).body(details);
    }

    @GetMapping("/details")
    public ResponseEntity<Map<String, Object>> detailHealth() {
        Map<String, Object> details = new LinkedHashMap<>();

        // CPU
        RuntimeMXBean runtime = ManagementFactory.getRuntimeMXBean();
        details.put("uptime", runtime.getUptime());
        details.put("process_cpu_usage", 
            OperatingSystemMXBean.class.cast(
                ManagementFactory.getOperatingSystemMXBean()).getCpuLoad());

        // Memory
        MemoryMXBean memory = ManagementFactory.getMemoryMXBean();
        MemoryHeapMemoryUsage heap = (MemoryHeapMemoryUsage) memory.getHeapMemoryUsage();
        details.put("memory_heap_used", heap.getUsed() / 1024 / 1024 + "MB");
        details.put("memory_heap_max", heap.getMax() / 1024 / 1024 + "MB");

        return ResponseEntity.ok(details);
    }
}
```

## 10. 性能优化

| 优化方向 | 方案 |
|----------|------|
| 数据库连接 | HikariCP 连接池 + 读写分离 (未来) |
| 缓存策略 | Redis 缓存热点数据 (用户信息、测评类型) |
| 数据库查询 | JPA 分页 + 索引优化 + 避免 N+1 查询 |
| API 响应 | GZip 压缩 + HTTP/2 多路复用 |
| 异步处理 | Kafka 消息 + 异步线程池 + 批量操作 |
| 安全 | TLS 1.3 最小化握手开销 + 连接复用 |

## 11. 监控与告警

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| JVM 内存 | Heap/Non-Heap 使用率 | >85% |
| 请求响应时间 | P50 / P95 | P95 >1s |
| 错误率 | HTTP 5xx 比例 | >1% |
| 数据库连接池 | 活跃连接数 | >80% 最大池 |
| Kafka 消费延迟 | Lag 消息数 | >1000 条 |