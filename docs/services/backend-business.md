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
│  │  │  Controller Layer (当前实现: User 模块)                │    │  │
│  │  │  - 用户管理 (已实现)                                   │    │  │
│  │  │  - 班级管理 / 测评任务 / 报告服务 / 订单支付 (规划中)   │    │  │
│  │  └───────────────────────────────────────────────────────┘    │  │
│  │                                                               │  │
│  │  ┌───────────────────────────────────────────────────────┐    │  │
│  │  │  Service Layer (当前实现: User 模块)                   │    │  │
│  │  │  - 用户服务 (已实现)                                   │    │  │
│  │  │  - 测评服务 / AI 服务接口 / 订单服务 (规划中)          │    │  │
│  │  └───────────────────────────────────────────────────────┘    │  │
│  │                                                               │  │
│  │  ┌───────────────────────────────────────────────────────┐    │  │
│  │  │  Repository Layer (当前实现: User 模块)                │    │  │
│  │  │  - MySQL (JPA) - UserRepository (已实现)              │    │  │
│  │  │  - MongoDB / Redis / Kafka (规划中)                   │    │  │
│  │  └───────────────────────────────────────────────────────┘    │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Data Layer                                      │
│  ┌──────────┐  ┌──────────┐                                         │
│  │  MySQL   │  │ MongoDB  │  (Redis / ClickHouse 规划中)            │
│  └──────────┘  └──────────┘                                         │
└─────────────────────────────────────────────────────────────────────┘
```

> **当前状态:** 仅 User 模块（用户 CRUD）已实现，其余模块处于规划阶段。

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
│   │   │   ├── controller/                    # 控制器
│   │   │   │   └── UserController.java        # 用户管理 (CRUD) [已实现]
│   │   │   │   # 其他 Controller (规划中):
│   │   │   │   # - AuthController.java        # 认证接口
│   │   │   │   # - ClassController.java       # 班级管理
│   │   │   │   # - AssessmentTaskController.java # 测评任务管理
│   │   │   │   # - ReportController.java      # 报告服务
│   │   │   │   # - OrderController.java       # 订单管理
│   │   │   │   # - PaymentController.java     # 支付接口
│   │   │   │   # - NotificationController.java # 通知推送
│   │   │   │   # - HealthController.java      # 健康检查
│   │   │   ├── service/                       # 业务逻辑
│   │   │   │   └── UserService.java           # 用户服务 [已实现]
│   │   │   │   # 其他 Service (规划中):
│   │   │   │   # - AuthService.java           # 认证服务
│   │   │   │   # - ClassService.java          # 班级服务
│   │   │   │   # - AssessmentService.java     # 测评服务
│   │   │   │   # - ReportService.java         # 报告服务
│   │   │   │   # - OrderService.java          # 订单服务
│   │   │   │   # - NotificationService.java   # 通知服务
│   │   │   ├── repository/                    # 数据访问层
│   │   │   │   └── UserRepository.java        # 用户 (MySQL) [已实现]
│   │   │   │   # 其他 Repository (规划中):
│   │   │   │   # - ClassRepository.java       # 班级 (MySQL)
│   │   │   │   # - AssessmentTaskRepository.java # 测评任务 (MySQL)
│   │   │   │   # - OrderRepository.java       # 订单 (MySQL)
│   │   │   │   # - EventRecordRepository.java # 事件记录 (MongoDB)
│   │   │   ├── entity/                        # 实体类
│   │   │   │   └── User.java                  # 用户实体 [已实现]
│   │   │   │   # 其他 Entity (规划中):
│   │   │   │   # - Class.java                 # 班级实体
│   │   │   │   # - AssessmentTask.java        # 测评任务实体
│   │   │   │   # - AssessmentResult.java      # 测评结果实体
│   │   │   │   # - Order.java                 # 订单实体
│   │   │   │   # - Subscription.java          # 订阅实体
│   │   │   │   # - Notification.java          # 通知实体
│   │   │   │   # - Organization.java          # 机构实体
│   │   │   │   # - EventRecord.java           # 事件记录 (MongoDB)
│   │   │   │   # dto/ (规划中)
│   │   │   │   # enums/ (规划中)
│   │   │   │   # exception/ (规划中)
│   │   │   │   # util/ (规划中)
│   │   │   └── resources/
│   │   │       └── application.yml            # 主配置文件
│   │   └── test/                              # 测试 (规划中)
│   └── README.md
```

> **说明:** 当前仅实现 User 模块的 Controller、Service、Repository、Entity 四个核心文件。其余模块均处于规划阶段，目录和文件尚未创建。

## 3. 数据库设计

### 3.1 当前实现: User 表

```sql
-- 用户表 (已实现)
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL, -- ADMIN, TEACHER, STUDENT, PARENT
    real_name VARCHAR(50),
    avatar VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 3.2 规划中的表

以下表结构为设计规划，尚未实现:

```sql
-- 家长学生关联表 (规划中)
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

-- 班级表 (规划中)
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

-- 班级成员表 (规划中)
CREATE TABLE class_members (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    class_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    role VARCHAR(20), -- STUDENT, TEACHER
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_class_member (class_id, user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 测评类型表 (规划中)
CREATE TABLE assessment_types (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    cognitive_dimension VARCHAR(50),
    duration_seconds INT,
    version VARCHAR(20),
    config JSON,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 测评任务表 (规划中)
CREATE TABLE assessment_tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    org_id BIGINT,
    class_id BIGINT,
    title VARCHAR(200) NOT NULL,
    type_code VARCHAR(50) NOT NULL,
    config JSON,
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

-- 测评结果表 (规划中)
CREATE TABLE assessment_results (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    task_id BIGINT,
    type_code VARCHAR(50) NOT NULL,
    request_id VARCHAR(100),
    session_id VARCHAR(100),
    score_data JSON,
    cognitive_profile JSON,
    ai_recommendations JSON,
    report_status VARCHAR(20) DEFAULT 'PENDING',
    status VARCHAR(20) DEFAULT 'FINISHED',
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_task (task_id),
    INDEX idx_status (report_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 3.3 MongoDB 集合设计 (规划中)

```javascript
// 事件记录集合 (规划中)
{
    _id: ObjectId,
    event_id: "event-xxxxx",
    user_id: 12345,
    session_id: "session-yyyyy",
    type: "CLICK | HOVER | KEY_DOWN | ASSESSMENT_START | ASSESSMENT_COMPLETE",
    task_id: "task-zzzzz",
    performance_start: 1234567.890123,
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

### 3.4 ClickHouse 表设计 (规划中)

```sql
CREATE TABLE event_records_ch (
    event_id String,
    user_id Int64,
    session_id String,
    type LowCardinality(String),
    task_id String,
    performance_start Decimal64(6),
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
    age_group String,
    created_at DateTime,
    request_id String
) ENGINE = MergeTree()
ORDER BY (user_id, created_at);
```

## 4. API 接口设计

### 4.1 当前实现: 用户管理接口

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/users` | 获取所有用户列表 | 无 (当前实现) |
| `GET` | `/api/v1/users/{id}` | 获取用户详情 | 无 (当前实现) |
| `POST` | `/api/v1/users` | 创建用户 | 无 (当前实现) |
| `PUT` | `/api/v1/users/{id}` | 更新用户信息 | 无 (当前实现) |
| `DELETE` | `/api/v1/users/{id}` | 删除用户 | 无 (当前实现) |

**请求/响应示例:**

```json
// GET /api/v1/users 响应
[
    {
        "id": 1,
        "username": "teacher01",
        "password": "secure-password",
        "role": "TEACHER",
        "realName": "张老师",
        "avatar": null,
        "createdAt": "2026-06-01T08:00:00",
        "updatedAt": "2026-06-01T08:00:00"
    }
]

// POST /api/v1/users 请求
{
    "username": "student01",
    "password": "password123",
    "role": "STUDENT",
    "realName": "李小明"
}

// POST /api/v1/users 响应
{
    "id": 2,
    "username": "student01",
    "password": "password123",
    "role": "STUDENT",
    "realName": "李小明",
    "avatar": null,
    "createdAt": "2026-06-07T08:00:00",
    "updatedAt": "2026-06-07T08:00:00"
}

// PUT /api/v1/users/1 请求
{
    "username": "teacher01",
    "realName": "张老师(已更新)",
    "role": "TEACHER",
    "avatar": "https://example.com/avatar.png"
}

// DELETE /api/v1/users/1 响应
// HTTP 200 OK (无响应体)
```

### 4.2 规划中的 API 接口

以下接口为设计规划，尚未实现:

#### 认证接口 (规划中)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/v1/auth/login` | 登录 (获取 JWT) | 无 |
| `POST` | `/api/v1/auth/refresh` | 刷新 token | Bearer Token |
| `POST` | `/api/v1/auth/logout` | 登出 | Bearer Token |
| `POST` | `/api/v1/auth/register` | 注册 (家长/教师) | 无 |

#### 班级管理接口 (规划中)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/classes` | 班级列表 (分页) | Bearer Token |
| `POST` | `/api/v1/classes` | 创建班级 | Bearer Token (Teacher/Manager) |
| `GET` | `/api/v1/classes/{id}` | 班级详情 | Bearer Token |
| `PUT` | `/api/v1/classes/{id}` | 更新班级 | Bearer Token (Teacher/Manager) |
| `GET` | `/api/v1/classes/{id}/members` | 班级成员列表 | Bearer Token |
| `POST` | `/api/v1/classes/{id}/members` | 添加成员 | Bearer Token (Teacher/Manager) |
| `DELETE` | `/api/v1/classes/{id}/members/{user_id}` | 移除成员 | Bearer Token (Teacher/Manager) |

#### 测评接口 (规划中)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/assessment/tasks` | 获取测评任务列表 | Bearer Token |
| `POST` | `/api/v1/assessment/tasks` | 创建测评任务 | Bearer Token (Teacher/Manager) |
| `GET` | `/api/v1/assessment/tasks/{id}` | 获取任务详情 | Bearer Token |
| `DELETE` | `/api/v1/assessment/tasks/{id}` | 删除测评任务 | Bearer Token (Manager) |
| `GET` | `/api/v1/assessment/results` | 获取测评结果列表 | Bearer Token |
| `GET` | `/api/v1/assessment/results/{id}` | 获取测评详情 | Bearer Token |
| `GET` | `/api/v1/assessment/available` | 获取可测试任务 | Bearer Token (Student) |

#### 报告接口 (规划中)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/reports` | 获取报告列表 | Bearer Token |
| `POST` | `/api/v1/reports/generate` | 生成 AI 报告 | Bearer Token (Teacher/Manager) |
| `GET` | `/api/v1/reports/{id}` | 获取报告详情 | Bearer Token |
| `POST` | `/api/v1/reports/{id}/feedback` | 提交反馈 | Bearer Token (Teacher) |

#### 订单支付接口 (规划中)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/orders` | 订单列表 (分页) | Bearer Token |
| `POST` | `/api/v1/orders` | 创建订单 | Bearer Token |
| `GET` | `/api/v1/orders/{order_no}` | 订单详情 | Bearer Token |
| `POST` | `/api/v1/payments/create` | 创建支付 | Bearer Token |
| `POST` | `/api/v1/payments/callback/wechat` | 微信支付回调 | 签名验证 |
| `POST` | `/api/v1/payments/callback/alipay` | 支付宝回调 | 签名验证 |

#### 订阅管理接口 (规划中)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/subscriptions` | 订阅详情 | Bearer Token |
| `POST` | `/api/v1/subscriptions/renew` | 续费订阅 | Bearer Token |
| `POST` | `/api/v1/subscriptions/cancel` | 取消订阅 | Bearer Token |
| `POST` | `/api/v1/subscriptions/reactivate` | 重新激活 | Bearer Token |

#### 运营接口 (规划中)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/stats/dashboard` | 仪表盘统计 | Bearer Token (Admin) |
| `GET` | `/api/v1/stats/users` | 用户统计 | Bearer Token (Admin) |
| `GET` | `/api/v1/stats/assessments` | 测评统计 | Bearer Token (Manager/Admin) |
| `GET` | `/api/v1/stats/financial` | 财务统计 | Bearer Token (Admin) |

### 4.3 统一响应格式 (规划中)

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

> **说明:** 当前实现直接返回实体对象，未封装统一响应格式。统一响应格式 (`ApiResponse`、`PageResponse`) 为规划内容。

## 5. 核心业务逻辑

### 5.1 当前实现: 用户服务

```java
// service/UserService.java (已实现)
@Service
@RequiredArgsConstructor
@Transactional
public class UserService {

    private final UserRepository userRepository;

    public List<User> findAll() {
        return userRepository.findAll();
    }

    public User findById(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new EntityNotFoundException("User not found with id: " + id));
    }

    public User save(User user) {
        return userRepository.save(user);
    }

    public User update(Long id, User updatedUser) {
        User existingUser = findById(id);
        existingUser.setUsername(updatedUser.getUsername());
        existingUser.setRealName(updatedUser.getRealName());
        existingUser.setRole(updatedUser.getRole());
        existingUser.setAvatar(updatedUser.getAvatar());
        return userRepository.save(existingUser);
    }

    public void delete(Long id) {
        userRepository.deleteById(id);
    }

    public User findByUsername(String username) {
        return userRepository.findByUsername(username)
            .orElseThrow(() -> new EntityNotFoundException("User not found with username: " + username));
    }
}
```

### 5.2 规划中的业务逻辑

以下业务逻辑为设计规划，尚未实现:

#### 用户认证服务 (规划中)

```java
// service/AuthService.java (规划中)
@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;

    public LoginResponse login(LoginRequest request) {
        User user = userRepository.findByUsername(request.username())
            .orElseThrow(() -> new BusinessException("Invalid credentials"));

        if (!passwordEncoder.matches(request.password(), user.getPassword())) {
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
        user.setPassword(passwordEncoder.encode(request.password()));
        user.setRole(request.role());
        user.setRealName(request.realName());

        userRepository.save(user);
    }
}
```

#### 测评结果处理流程 (规划中)

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

#### 报告服务 - AI 报告生成 (规划中)

```java
// service/ReportService.java (规划中)
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

#### 订单状态机 (规划中)

```java
// enums/OrderStatus.java (规划中)
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

// service/OrderService.java (规划中)
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

## 6. 安全设计 (规划中)

### 6.1 Spring Security 配置 (规划中)

```java
// config/SecurityConfig.java (规划中)
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

### 6.2 JWT 认证过滤器 (规划中)

```java
// config/JwtAuthenticationFilter.java (规划中)
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

### 6.3 未成年用户合规脱敏 (规划中)

```java
// util/ComplianceUtils.java (规划中)
@Component
public class ComplianceUtils {

    public User sanitizeForAi(User user) {
        User sanitized = new User();
        sanitized.setId(user.getId());
        sanitized.setUsername(anonymize(user.getUsername()));
        sanitized.setRole(user.getRole());
        sanitized.setRealName(anonymize(user.getRealName()));
        sanitized.setPhone(maskPhone(user.getPhone()));
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
}
```

> **说明:** 当前 `pom.xml` 已引入 `spring-boot-starter-security` 和 `jjwt` 依赖，但安全配置类 (`SecurityConfig.java`、`JwtAuthenticationFilter.java`、`JwtService.java`) 尚未实现。当前 User 模块的 API 端点未启用认证拦截。

## 7. 异步处理机制 (规划中)

### 7.1 Kafka 消息主题 (规划中)

| 主题 | 生产者 | 消费者 | 描述 |
|------|--------|--------|------|
| `event.ingestion` | Go 网关 | Java 后端 | 事件数据流入 |
| `event.processing` | Java 后端 | Java 后端 (ClickHouse 写入) | 事件聚合与存储 |
| `report.generation` | Java 后端 | Java 后端 (触发 AI) | 请求 AI 生成报告 |
| `report.complete` | AI 服务 | Java 后端 | 报告生成完成回调 |
| `notification.push` | Java 后端 | 通知服务 | 消息推送 |
| `payment.completed` | 支付网关 | Java 后端 | 支付成功回调 |

### 7.2 异步事件处理 (规划中)

```java
// config/AsyncConfig.java (规划中)
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

// service/EventProcessingService.java (规划中)
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

> **说明:** 当前 `pom.xml` 未引入 Kafka 依赖，异步处理机制尚未实现。

## 8. 配置文件

### 8.1 当前配置 (`application.yml`)

```yaml
server:
  port: 8080

spring:
  application:
    name: backend-business

  # Database
  datasource:
    url: jdbc:mysql://localhost:3306/brainspark?useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true
    username: root
    password: ${DB_PASSWORD:password}
    driver-class-name: com.mysql.cj.jdbc.Driver

  # JPA
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: false
    properties:
      hibernate:
        dialect: org.hibernate.dialect.MySQLDialect

  # MongoDB
  data:
    mongodb:
      uri: mongodb://localhost:27017/brainspark

  # Security (JWT)
  security:
    jwt:
      secret: ${JWT_SECRET:mySecretKeyChangeInProduction}
      expiration: 86400000

# Custom
brainspark:
  ai:
    api-url: ${AI_API_URL:http://localhost:8001}
```

### 8.2 规划中的配置文件

以下配置文件为设计规划，尚未创建:

- `application-dev.yml` - 开发环境配置
- `application-prod.yml` - 生产环境配置

## 9. 部署与运维

### 9.1 Docker 配置

```dockerfile
# docker/Dockerfile (已实现)
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

### 9.2 健康检查端点 (规划中)

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

## 10. 性能优化 (规划中)

| 优化方向 | 方案 |
|----------|------|
| 数据库连接 | HikariCP 连接池 + 读写分离 (未来) |
| 缓存策略 | Redis 缓存热点数据 (用户信息、测评类型) |
| 数据库查询 | JPA 分页 + 索引优化 + 避免 N+1 查询 |
| API 响应 | GZip 压缩 + HTTP/2 多路复用 |
| 异步处理 | Kafka 消息 + 异步线程池 + 批量操作 |
| 安全 | TLS 1.3 最小化握手开销 + 连接复用 |

> **说明:** 当前 User 模块数据量较小，尚未启用性能优化措施。

## 11. 监控与告警 (规划中)

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| JVM 内存 | Heap/Non-Heap 使用率 | >85% |
| 请求响应时间 | P50 / P95 | P95 >1s |
| 错误率 | HTTP 5xx 比例 | >1% |
| 数据库连接池 | 活跃连接数 | >80% 最大池 |
| Kafka 消费延迟 | Lag 消息数 | >1000 条 |

> **说明:** 监控与告警机制尚未实现。

## 附录: 实现状态总览

| 模块 | Controller | Service | Repository | Entity | 状态 |
|------|-----------|---------|------------|--------|------|
| 用户管理 (User) | ✅ | ✅ | ✅ | ✅ | **已实现** |
| 认证 (Auth) | ❌ | ❌ | - | - | 规划中 |
| 班级管理 (Class) | ❌ | ❌ | ❌ | ❌ | 规划中 |
| 测评任务 (Assessment) | ❌ | ❌ | ❌ | ❌ | 规划中 |
| 测评结果 (Result) | ❌ | ❌ | ❌ | ❌ | 规划中 |
| 报告 (Report) | ❌ | ❌ | ❌ | ❌ | 规划中 |
| 订单 (Order) | ❌ | ❌ | ❌ | ❌ | 规划中 |
| 支付 (Payment) | ❌ | ❌ | - | - | 规划中 |
| 订阅 (Subscription) | ❌ | ❌ | ❌ | ❌ | 规划中 |
| 通知 (Notification) | ❌ | ❌ | ❌ | ❌ | 规划中 |
| 运营统计 (Stats) | ❌ | ❌ | - | - | 规划中 |
| 机构 (Organization) | ❌ | ❌ | - | ❌ | 规划中 |
| 事件记录 (Event) | - | ❌ | ❌ | ❌ | 规划中 |
| 安全配置 (Security) | - | ❌ | - | - | 规划中 |
| 健康检查 (Health) | ❌ | - | - | - | 规划中 |