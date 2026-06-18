-- BrainSpark ClickHouse 初始化脚本
-- 开发环境使用

-- 创建分析数据库
CREATE DATABASE IF NOT EXISTS brainspark_analytics;

-- 使用分析数据库
USE brainspark_analytics;

-- 用户原始测评事件表
CREATE TABLE IF NOT EXISTS assessment_event_records (
    event_id String,
    user_id Int64,
    session_id String,
    type_code String,
    event_type String,
    performance_now Float64,
    reaction_time_ms Int32,
    pointer_x Int32,
    pointer_y Int32,
    device_info String,
    created_at DateTime
) ENGINE = MergeTree()
ORDER BY (user_id, created_at)
PARTITION BY toYYYYMM(created_at)
TTL created_at + INTERVAL 90 DAY;

-- 用户测评结果聚合表
CREATE TABLE IF NOT EXISTS assessment_results_agg (
    user_id Int64,
    type_code String,
    session_id String,
    total_score Float64,
    avg_reaction_time Float64,
    accuracy_rate Float64,
    task_count Int32,
    started_at DateTime,
    completed_at DateTime
) ENGINE = MergeTree()
ORDER BY (user_id, started_at)
PARTITION BY toYYYYMM(started_at);

-- 教育常模表
CREATE TABLE IF NOT EXISTS cognitive_normalize (
    dimension String,
    age_group String,
    mean_score Float64,
    std_deviation Float64,
    sample_size Int32,
    percentile_25 Float64,
    percentile_50 Float64,
    percentile_75 Float64,
    updated_at DateTime
) ENGINE = MergeTree()
ORDER BY (dimension, age_group);

-- 教育知识表
CREATE TABLE IF NOT EXISTS education_knowledge (
    id Int64,
    category String,
    title String,
    content String,
    tags Array(String),
    created_at DateTime
) ENGINE = MergeTree()
ORDER BY (category, created_at)
PARTITION BY toYYYYMM(created_at);

-- 常模版本管理表
CREATE TABLE IF NOT EXISTS normalize_version (
    id Int64,
    version String,
    description String,
    effective_date Date,
    created_at DateTime
) ENGINE = MergeTree()
ORDER BY (id);