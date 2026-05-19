# BrainSpark 基础设施与部署架构详细设计

> 本文档详细描述 BrainSpark 平台的基础设施层设计，包括 MySQL/MongoDB/Redis/Kafka/ClickHouse/Milvus 数据库集群架构、Docker Compose 编排方案、K8s 部署模板以及 CI/CD 流水线设计。

## 1. 基础设施架构总览

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Cloud / On-Prem                           │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Kubernetes Cluster (K8s)                     │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │  │
│  │  │ Student  │ │ Parent  │ │  Teacher │ │ Operator │            │  │
│  │  │ Web(Pod) │ │ Web(Pod)│ │  Web(Pod)│ │  Web(Pod)│            │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘            │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │  │
│  │  │ Gateway  │ │ Business│ │   AI     │ │ Nginx/  │            │  │
│  │  │  (Pod)   │ │  (Pod)  │ │  (Pod)   │ │ Ingress │            │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘            │  │
│  │                                                               │  │
│  │  ┌────────────────────── StatefulSets ─────────────────────┐  │  │
│  │  │ Kafka │ ClickHouse │ Milvus │ MongoDB │ Redis │ MySQL  │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────── Monitoring ──────────────────────────┐ │
│  │  Prometheus + Grafana + Loki + Jaeger (Trace) + ELK (Log)         │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌────────────────────── CI/CD Pipeline ───────────────────────────┐ │
│  │  GitHub Actions / GitLab CI ──► Build ──► Test ──► Push Image ──► Deploy via Helm  │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌────────────────── External Services ────────────────────────────┐ │
│  │  Stripe │ WeChat Pay │ Alipay │ Qwen OpenAI │ SMS / Email       │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. MySQL 集群架构 (业务核心数据存储)

### 2.1 部署策略

BrainSpark 业务服务 `backend-business` 使用 MySQL 8.0 作为主存储：
- **开发环境**: 单实例 Docker 部署。
- **预发环境**: 双实例 (Master-Slave 主从复制，手动读写分离)。
- **生产环境**: 高可用集群 (基于 [MySQL InnoDB Cluster](https://dev.mysql.com/doc/refman/8.0/en/mysql-innodb-cluster.html) 或托管云服务 AWS Aurora RDS / Google Cloud SQL)。

### 2.2 MySQL 逻辑库设计 (ER Schema)

```sql
-- ============================================
-- 1. 用户 & 合规库 (users_schema)
-- ============================================

CREATE TABLE users_schema.account_users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    password_hash VARCHAR(128),                  -- BCrypt 加密
    email VARCHAR(128),
    phone VARCHAR(20),
    role LowCardinalityVARCHAR(20),              -- ADMIN, TEACHER, PARENT, STUDENT
    is_minor TINYINT DEFAULT 0,                  -- 是否为未成年人 (用于合规判断)
    guardian_id BIGINT,                          -- 未成年人的监护人 id (外键)
    is_active TINYINT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    INDEX idx_email (email),
    INDEX idx_phone (phone)
);

CREATE TABLE users_schema.guardian_consent (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    guardian_user_id BIGINT NOT NULL,
    child_user_id BIGINT NOT NULL,
    consent_given TINYINT DEFAULT 0,
    consent_at TIMESTAMP NULL,
    consent_method LowCardinalityVARCHAR(20),    -- WEB_FORM, PAPER_SCANNED
    consent_proof VARCHAR(255),                  -- PDF file path
    is_active TINYINT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_guardian_child (guardian_user_id, child_user_id),
    INDEX idx_consent_given (consent_given)
);


-- ============================================
-- 2. 测评业务库 (assessment_schema)
-- ============================================

-- 学生信息 (脱敏)
CREATE TABLE assessment_schema.students (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    real_name VARCHAR(32),                       -- 仅在服务端保存 (脱敏显示: "张*三")
    name_hash VARCHAR(64) UNIQUE NOT NULL,       -- 姓名哈希值，用于登录查询
    birth_year YEAR,                              -- 出生年份 (仅用于年龄分组，存年份不存具体日期)
    gender TINYINT,                               -- 1: 男, 2: 女, 0: 未知
    classroom_code VARCHAR(20),                   -- 班级标识
    school_name VARCHAR(128),                     -- 学校名称
    parent_guardian_name VARCHAR(64),             -- 家长 / 监护人姓名
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_birth_year (birth_year),
    INDEX idx_classroom (classroom_code)
);

-- 家长账号
CREATE TABLE assessment_schema.parents (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    account_id BIGINT NOT NULL,                    -- 关联 account_users
    child_student_id BIGINT NOT NULL,
    relationship VARCHAR(20),                      -- PARENT_GUARDIAN, TEACHER_OBSERVER
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_account (account_id),
    UNIQUE KEY uk_child (child_student_id)
);

-- 测评任务 (分发记录)
CREATE TABLE assessment_schema.assessment_tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_code VARCHAR(32) UNIQUE NOT NULL,         -- SHULTER_5X5_DAY_001
    type_code LowCardinalityVARCHAR(32),           -- VISUAL_ATTENTION, WORKING_MEMORY
    difficulty_level TINYINT,                      -- 1-3 难度
    target_age_min TINYINT,                        -- 目标最小年龄
    target_age_max TINYINT,                        -- 目标最大年龄
    max_attempts TINYINT DEFAULT 3,                -- 最多尝试次数
    is_published TINYINT DEFAULT 0,
    created_by BIGINT,                             -- TEACHER id
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP NULL
);

-- 学生任务分发 (Teacher 布置 -> 学生执行)
CREATE TABLE assessment_schema.task_assignments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_code VARCHAR(32) NOT NULL,
    class_room_code VARCHAR(20),                   -- 按班级批量分发
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date DATE,
    INDEX idx_classroom (class_room_code, due_date)
);

CREATE TABLE assessment_schema.student_task_assignments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    assignment_id BIGINT NOT NULL,                 -- 父表 task_assignments
    student_id BIGINT NOT NULL,
    status LowCardinalityVARCHAR(20) DEFAULT 'PENDING', -- PENDING, IN_PROGRESS, COMPLETED, EXPIRED
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    INDEX idx_student_status (student_id, status)
);

-- 测评会话 (每次尝试)
CREATE TABLE assessment_schema.assessment_sessions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id CHAR(36) UNIQUE NOT NULL,           -- UUID
    task_code VARCHAR(32) NOT NULL,
    student_id BIGINT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NULL,
    total_time_sec FLOAT,                          -- 总耗时
    grid_size TINYINT,                             -- 如 5x5
    is_completed TINYINT DEFAULT 0,
    INDEX idx_student_task (student_id, task_code)
);

-- 测评行为记录 (ClickHouse 处理过后再回写摘要)
CREATE TABLE assessment_schema.event_summaries (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id CHAR(36) NOT NULL,
    event_type LowCardinalityVARCHAR(20),          -- CLICK, HOVER, COMPLETE
    grid_cell TINYINT,
    reaction_time_ms SMALLINT,
    is_correct TINYINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session (session_id)
);

-- 测评结果与报告
CREATE TABLE assessment_schema.assessment_results (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id CHAR(36) UNIQUE NOT NULL,
    type_code VARCHAR(32),
    target_age_group VARCHAR(20),                  -- "6-8"
    avg_reaction_time_ms SMALLINT,                 -- 平均反应时
    correct_count TINYINT,                         -- 正确数
    total_clicks TINYINT,                          -- 总点击
    validity_status LowCardinalityVARCHAR(20),     -- VALID, FLAGGED, INVALID
    report_generated TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================
-- 3. 商城与订单库 (mall_schema)
-- ============================================

CREATE TABLE mall_schema.products (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sku_code VARCHAR(32) UNIQUE NOT NULL,
    name VARCHAR(128) NOT NULL,
    description TEXT,
    price_cents INT NOT NULL,                      -- 存储分为 (¥10.00 → 1000)
    currency CHAR(3) DEFAULT 'CNY',
    stripe_price_id VARCHAR(128),                  -- Stripe 商品 ID
    wechat_pay_product_id VARCHAR(128),
    status LowCardinalityVARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE mall_schema.orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(32) UNIQUE NOT NULL,          -- 全局订单号
    user_id BIGINT NOT NULL,
    student_id BIGINT,                             -- 如果是家长购买给学生
    product_sku VARCHAR(32) NOT NULL,
    amount_cents INT NOT NULL,
    status LowCardinalityVARCHAR(20) DEFAULT 'PENDING_PAYMENT', -- PENDING, PAID, COMPLETED, REFUNDED, CANCELLED
    payment_channel LowCardinalityVARCHAR(20),     -- STRIPE, WECHAT, ALIPAY
    payment_intent_id VARCHAR(128),                -- Stripe / 微信 / 支付宝 流水号
    paid_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE mall_schema.subscription_plans (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    plan_type VARCHAR(32) NOT NULL,                -- MONTHLY, QUARTERLY, YEARLY
    price_cents INT NOT NULL,
    stripe_price_id VARCHAR(128),
    status TINYINT DEFAULT 1,
    expires_at_offset_days INT                     -- 自动续期的天数偏移
);


-- ============================================
-- 4. AI 服务库 (ai_schema)
-- ============================================

CREATE TABLE ai_schema.knowledge_base (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    doc_id VARCHAR(64) UNIQUE NOT NULL,
    doc_title VARCHAR(200),
    category VARCHAR(50),
    tags ARRAY VARCHAR(128),                       -- VARCHAR 存储标签
    embedding_dim TINYINT DEFAULT 1536,
    version INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ai_schema.reports (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    result_id BIGINT NOT NULL,                     -- 来自 assessment_results
    user_id BIGINT NOT NULL,                       -- 查看报告的用户 id
    report_type LowCardinalityVARCHAR(32),         -- INDIVIDUAL (个体), CLASS_OVERVIEW (班级报告), DEVELOPMENT (发展预测)
    report_json LONGTEXT,                          -- 生成的完整 JSON 报告
    version INT DEFAULT 1,
    is_official TINYINT DEFAULT 0,                 -- 是否教师/家长已签署
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_result (result_id)
);


-- ============================================
-- MySQL 部署 (Docker Compose)
-- ============================================
```

```yaml
# infrastructure/docker/docker-compose.yml - MySQL 部分
services:
  mysql-primary:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: brainspark
      MYSQL_USER: brainspark
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init-scripts:/docker-entrypoint-initdb.d
    command: >
      --default-authentication-plugin=caching_sha2_password
      --binlog-format=ROW
      --log-bin=mysql-bin
      --server-id=1

volumes:
  mysql_data:
```

## 3. ClickHouse 集群架构 (分析 & 常模存储)

### 3.1 ClickHouse 部署模式
- **开发环境**: 单实例 Docker 部署。
- **生产环境**: 
    - **SHARD** (分片): 3 副本模式 (3 shards × 2 replicas = 6 nodes), 数据根据 `user_id` hash 分片。
    - **ZooKeeper / ClickHouse Keeper**: 用于分布式表和副本同步。

### 3.2 ClickHouse 数据库与表

```sql
-- 创建业务数据库
CREATE DATABASE IF NOT EXISTS brainspark_analytics;

USE brainspark_analytics;

-- 原始事件表
CREATE TABLE assessment_event_records (
    event_id String,
    user_id Int64,
    session_id String,
    task_id String,
    type_code LowCardinality(String),
    event_type LowCardinality(String),
    grid_cell UInt8,
    performance_now Decimal64(6),
    reaction_time_ms UInt16,
    pointer_x Float32,
    pointer_y Float32,
    correct UInt8,
    created_at DateTime,
    request_id String
) ENGINE = MergeTree()
ORDER BY (user_id, created_at)
SETTINGS index_granularity = 8192;

-- 聚合结果表
CREATE TABLE assessment_results_agg (
    result_id String,
    user_id Int64,
    session_id String,
    type_code LowCardinality(String),
    total_clicks UInt32,
    correct_clicks UInt32,
    avg_reaction_time_ms UInt16,
    sd_reaction_time_ms Float32,
    total_time_sec Float32,
    score_value Float32,
    is_flagged UInt8 DEFAULT 0,
    validity_status LowCardinality(String),
    started_at DateTime,
    completed_at DateTime,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (user_id, started_at);

-- 教育常模表
CREATE TABLE cognitive_normalize (
    id UInt64,
    age_group LowCardinality(String),
    dimension LowCardinality(String),
    score_mean Float32,
    score_std Float32,
    p25 Float32,
    p50 Float32,
    p75 Float32,
    p95 Float32,
    n UInt32,
    updated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (dimension, age_group);
```

## 4. Redis 集群架构 (缓存、Token 与限流)

### 4.1 部署模式
- **生产**: Redis 6+ Sentinel 模式或 Redis Cluster (3 master + 3 replica)。
- **开发**: 单节点。

### 4.2 Key 设计规范

```text
# JWT Token & Session 管理
jwt:whitelist:<jti>                 -> 1 (TTL: token remaining life)
jwt:blacklist:<jti>                 -> 1 (TTL: token remaining life)
session:user:<user_id>              -> JSON (TTL: 30d)

# API 限流
rate_limit:gateway:<ip>             -> counter (TTL: 60s, MAX 500 QPS)
rate_limit:gateway:<api_path>:<user_id> -> counter (TTL: 60s, MAX 100 QPS)

# Kafka Message Offset (用于报告生成防重)
report:pending:<user_id>:<type_code>  -> 1 (TTL: 5min)

# 评测锁
assessment:lock:<session_id>          -> {"status": "IN_PROGRESS", "last_update": <ts>}
                                          TTL: 15min
```

## 5. MongoDB 集群 (原始行为与日志)

MongoDB 用于存储海量、高并发的行为点数据，因为事件结构是半结构化，且数据量大 (原始轨迹、压力值)。

### 5.1 Collection 设计

```javascript
// event_records 集合 (Flink 写入)
{
  _id: ObjectId("64e..."),
  event_id: "evt_abc123",
  user_id: NumberLong(12345),
  session_id: "ses_xyz789",
  task_id: "task_shulter_5x5",
  type_code: "VISUAL_ATTENTION",
  event_type: "CLICK",              // CLICK, HOVER, NAVIGATE, PRESS, RELEASE
  performance_now: 1234.567890,     // decimal-like float
  reaction_time_ms: NumberInt(420),
  pointer_x: 450.123,
  pointer_y: 300.456,
  pressure: 0.5,                    // 仅移动端可用
  device_info: {
    screen_width: NumberInt(1920),
    screen_height: NumberInt(1080),
    pixel_ratio: 1.5,
    browser: "Chrome",
    os: "Windows 11"
  },
  created_at: NumberLong(1715000000000), // Unix millis
  metadata: {
    version: "1.0.0",
    extra_field: "some_value"
  }
}

// 索引设置
db.event_records.createIndex({ "user_id": 1, "created_at": -1 })
db.event_records.createIndex({ "session_id": 1 })
db.event_records.createIndex({ "created_at": 1 }, { expireAfterSeconds: 2592000 }) // 30 天过期
```

## 6. Docker Compose (开发与测试编排)

完整的 `docker-compose.yml` 编排所有依赖服务和基础应用。

```yaml
# infrastructure/docker/docker-compose.yml

version: "3.9"

volumes:
  mysql_data:
  clickhouse_data:
  mongo_data:
  redis_data:
  kafka_data:
  zookeeper_data:

services:
  # ------------------ 开发用数据层 ------------------
  mysql:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: brainspark
      MYSQL_USER: brainspark
      MYSQL_PASSWORD: brainspark123
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ../../docs/db-init-scripts:/docker-entrypoint-initdb.d

  clickhouse:
    image: clickhouse/clickhouse-server:23.8
    restart: always
    ports:
      - "8123:8123"
      - "9000:9000"
    volumes:
      - clickhouse_data:/var/lib/clickhouse

  mongo:
    image: mongo:6
    restart: always
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  redis:
    image: redis:7-alpine
    restart: always
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    restart: always
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    volumes:
      - zookeeper_data:/var/lib/zookeeper/data

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    restart: always
    ports:
      - "9092:9092"
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0

  milvus:
    image: milvusdb/milvus:v2.3.4
    restart: always
    command: milvus run standalone
    ports:
      - "19530:19530"
      - "9091:9091"
    depends_on:
      - etcd
      - minio

  etcd:
    image: quay.io/coreos/etcd:v3.5.11
    restart: always
    ports:
      - "2379:2379"

  minio:
    image: minio/minio:latest
    restart: always
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - s3_data:/minio_data
    command: server /minio_data --console-address ":9001"

  # ------------------ 应用层 ------------------
  gateway-go:
    build:
      context: ../../apps/backend-gateway
      dockerfile: docker/Dockerfile.dev
    ports:
      - "8080:8080"
      - "8081:8081"
    environment:
      KAFKA_URI: kafka:9092
      REDIS_URI: redis:6379
      MONGO_URI: mongodb://mongo:27017

  business-java:
    build:
      context: ../../apps/backend-business
      dockerfile: docker/Dockerfile.dev
    ports:
      - "8088:8088"
    environment:
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/brainspark
      REDIS_HOST: redis
      KAFKA_BROKER: kafka:9092
      CLICKHOUSE_HOST: clickhouse
      MILVUS_HOST: milvus
      MILVUS_PORT: "19530"

  ai-service-python:
    build:
      context: ../../apps/ai-service
      dockerfile: docker/Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      LLM_API_KEY: ${LLM_API_KEY}
      MILVUS_HOST: milvus
      CLICKHOUSE_HOST: clickhouse
      REDIS_HOST: redis

  # ------------------ Web 应用层 (本地开发反向代理) ------------------
  # 在开发中，Vue 应用通常使用 vite devserver；部署时可通过 Nginx 统一反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ../nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - gateway-go
```

## 7. K8s 部署架构与 Helm Chart

### 7.1 Namespace 规划

```yaml
# 开发环境: namespace dev
# 预发环境: namespace staging
# 生产环境: namespace production
```

### 7.2 Deployment 模板 (business-java 示例)

```yaml
# infrastructure/k8s/business-java/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-business
  namespace: ${NAMESPACE}
  labels:
    app: backend-business
    tier: middleware
spec:
  replicas: ${REPLICAS:3}
  selector:
    matchLabels:
      app: backend-business
  template:
    metadata:
      labels:
        app: backend-business
    spec:
      containers:
        - name: business-service
          image: ${REGISTRY_URL}/brainspark/business:${VERSION}
          ports:
            - containerPort: 8088
          env:
            - name: SPRING_DATASOURCE_URL
              valueFrom:
                secretKeyRef:
                  name: business-db-secret
                  key: datasource-url
            - name: SPRING_DATA_REDIS_HOST
              value: "redis-master"
            - name: KAFKA_BROKER
              value: "kafka-broker"
            - name: MILVUS_HOST
              value: "milvus-coordinator"
            - name: CLICKHOUSE_HOST
              value: "clickhouse-server"
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /actuator/health
              port: 8088
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /actuator/health
              port: 8088
            initialDelaySeconds: 15
            periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: backend-business-svc
  namespace: ${NAMESPACE}
spec:
  selector:
    app: backend-business
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8088
  type: ClusterIP
```

### 7.3 Ingress 路由

```yaml
# infrastructure/k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: brainspark-ingress
  namespace: ${NAMESPACE}
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/use-regex: "true"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - brainspark.example.com
      secretName: brainspark-tls
  rules:
    - host: brainspark.example.com
      http:
        paths:
          - path: /api/student
            pathType: Prefix
            backend:
              service:
                name: student-web-svc
                port:
                  number: 80
          - path: /api/parent
            pathType: Prefix
            backend:
              service:
                name: parent-web-svc
                port:
                  number: 80
          - path: /api/teacher
            pathType: Prefix
            backend:
              service:
                name: teacher-web-svc
                port:
                  number: 80
          - path: /api/v[0-9]+
            pathType: Prefix
            backend:
              service:
                name: gateway-svc
                port:
                  number: 8080
```

## 8. Prometheus 与监控体系

```yaml
# infrastructure/monitoring/prometheus/scrape-config.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "business-java"
    metrics_path: "/actuator/prometheus"
    static_configs:
      - targets: ["business-java-svc:80"]

  - job_name: "gateway-go"
    static_configs:
      - targets: ["gateway-go-svc:8080"]

  - job_name: "ai-service-python"
    static_configs:
      - targets: ["ai-service-svc:8000"]

  - job_name: "clickhouse"
    static_configs:
      - targets: ["clickhouse-server:9363"]
```

## 9. 数据库备份与灾难恢复

### 9.1 MySQL 备份策略

```yaml
# infrastructure/scripts/mysql-backup.sh
#!/bin/bash
BACKUP_DIR="/backup/mysql"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mysqldump \
    --host=mysql-master \
    --user=root \
    --password="$MYSQL_ROOT_PASSWORD" \
    --all-databases \
    --single-transaction \
    --master-data=2 \
    --routines \
    --triggers > ${BACKUP_DIR}/full_backup_${TIMESTAMP}.sql

# 每日凌晨 2 点通过 cron 执行 (K8s CronJob)
# 保留 7 天本地快照
find ${BACKUP_DIR} -name "*.sql" -mtime +7 -delete
```

### 9.2 ClickHouse 备份策略

```xml
<!-- clickhouse-config.xml backup section -->
<yandex>
    <backup_dir>/var/lib/clickhouse/backups</backup_dir>
    <!-- 每日执行 clickhouse-backup 全量备份 -->
    <!-- 每周将 SQL 备份推送到 AWS S3 -->
    <s3>
        <endpoint>https://s3.amazonaws.com/brainspark-backups</endpoint>
        <bucket>brainspark-clickhouse-backups</bucket>
        <region>us-east-1</region>
        <max_retention_days>30</max_retention_days>
    </s3>
</yandex>
```

## 10. CI/CD 流水线设计

### 10.1 GitHub Actions 配置 (完整 CI/CD Pipeline)

```yaml
# .github/workflows/build-and-deploy.yml
name: BrainSpark CI/CD Pipeline

on:
  push:
    branches: [main, develop, "release/*"]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_TAG: ${{ github.sha }}

jobs:
  # ============================================
  # 1. Code Lint & Check
  # ============================================
  lint-and-check:
    name: Lint & Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: "pnpm"
      
      - name: Install dependencies
        run: pnpm install --frozen-lockfile
      
      - name: Frontend Lint (Student Web)
        run: pnpm --filter @brainspark/student lint
      
      - name: Frontend Lint (Teacher Web)
        run: pnpm --filter @brainspark/teacher lint
      
      - name: TypeScript Type Check
        run: pnpm --filter @brainspark/student type-check && pnpm --filter @brainspark/teacher type-check

  # ============================================
  # 2. Run Unit & Integration Tests
  # ============================================
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    needs: lint-and-check
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
        ports:
          - 3306:3306
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v4
      
      - name: Backend Java Unit Tests
        run: cd apps/backend-business && mvn test
        env:
          MYSQL_ROOT_PASSWORD: root
          REDIS_URI: localhost:6379

  # ============================================
  # 3. Build Docker Images
  # ============================================
  build-and-push:
    name: Build & Push Docker Images
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/release'))
    permissions:
      contents: read
      packages: write
    
    strategy:
      matrix:
        include:
          - app: backend-gateway
            context: apps/backend-gateway
          - app: backend-business
            context: apps/backend-business
          - app: ai-service
            context: apps/ai-service
          - app: student-web
            context: apps/student-web
          - app: parent-web
            context: apps/parent-web
          - app: teacher-web
            context: apps/teacher-web

    steps:
      - uses: actions/checkout@v4
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push ${{ matrix.app }}
        run: |
          docker build -t ${{ env.REGISTRY }}/brainspark/${{ matrix.app }}:${{ env.IMAGE_TAG }} \
            -t ${{ env.REGISTRY }}/brainspark/${{ matrix.app }}:latest \
            --file ${{ matrix.context }}/docker/Dockerfile ${{ matrix.context }}
          docker push ${{ env.REGISTRY }}/brainspark/${{ matrix.app }}:${{ env.IMAGE_TAG }}
          docker push ${{ env.REGISTRY }}/brainspark/${{ matrix.app }}:latest

  # ============================================
  # 4. Deploy (Staging / Production)
  # ============================================
  deploy:
    name: Deploy to K8s
    runs-on: ubuntu-latest
    needs: build-and-push
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://brainspark.example.com
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Helm
        uses: azure/setup-helm@v3
      
      - name: Configure Kubeconfig
        uses: azure/k8s-login-action@v1
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG }}
      
      - name: Deploy via Helm
        run: |
          helm upgrade --install brainspark-core infrastructure/helm/brainspark-core \
            --namespace production \
            --set image.tag=${{ env.IMAGE_TAG }} \
            --set environment=production \
            --wait --timeout 10m
```

### 10.2 Helm Chart 模板概览

```
infrastructure/helm/brainspark-core/
├── Chart.yaml              # 版本和基本信息
├── values.yaml             # 全局默认值 (namespace, replicas, image)
├── values-production.yaml  # 生产环境覆盖值 (更大 replicas, GPU, 生产数据库)
├── templates/
│   ├── _helpers.tpl        # 辅助模板 (命名、标签)
│   ├── deployment-gateway.yaml
│   ├── deployment-business.yaml
│   ├── deployment-ai-service.yaml
│   ├── deployment-nginx.yaml
│   ├── service-gateway.yaml
│   ├── service-business.yaml
│   ├── ingress.yaml
│   └── secret-db.yaml
```

```yaml
# infrastructure/helm/brainspark-core/values.yaml
image:
  registry: ghcr.io
  tag: latest

replicas:
  gateway: 2
  business: 2
  ai_service: 2
  web_app: 3

ingress:
  enabled: true
  host: brainspark.staging.example.com

resources:
  gateway:
    cpu: 250m
    memory: 256Mi
  business:
    cpu: 500m
    memory: 512Mi
```

---

## 11. 环境划分与数据隔离

| 环境 | 用途 | K8s Namespace | DB 实例 | 外部服务 Key |
|------|------|-------------|---------|--------------|
| `dev` | 本地联调 / Agent 自动化测试 | `dev` | Docker Compose 单实例 | 共享测试 API Key |
| `staging` | 预发 / UAT 验收 | `staging` | 单实例 (副本) | 测试环境 API Key |
| `production` | 正式环境 | `production` | 高可用集群 / 云托管 | 生产环境 API Key |

---

> **总结**: 基础设施层为 BrainSpark 平台提供稳定可靠的容器化运行时，通过 Docker Compose 满足开发和测试需求，通过 K8s + Helm 实现生产环境的弹性扩缩容和高可用部署，并通过 GitHub Actions 构建自动化 CI/CD 流水线，确保全生命周期质量管控。