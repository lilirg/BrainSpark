-- BrainSpark ClickHouse 分析型数据库初始化
-- 基于 docs/architecture/data-model.md 定义

-- 行为事件记录表
CREATE TABLE IF NOT EXISTS assessment_event_records (
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
    request_id String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (user_id, created_at)
TTL created_at + INTERVAL 30 DAY
SETTINGS index_granularity = 8192;

-- 添加跳数索引
ALTER TABLE assessment_event_records ADD INDEX idx_user_time (user_id, created_at) TYPE minmax GRANULARITY 4;

-- 测评结果聚合表
CREATE TABLE IF NOT EXISTS assessment_results_agg (
    result_id String,
    user_id Int64,
    session_id String,
    task_id String,
    type_code LowCardinality(String),
    total_clicks UInt32,
    correct_clicks UInt32,
    avg_reaction_time_ms UInt16,
    min_reaction_time_ms UInt16,
    p50_reaction_time_ms UInt16,
    p95_reaction_time_ms UInt16,
    sd_reaction_time_ms Float32,
    total_path_length Float32,
    avg_path_angle Float32,
    grid_size UInt8,
    total_time_sec Float32,
    score_value Float32,
    is_flagged UInt8 DEFAULT 0,
    flag_type LowCardinality(String),
    validity_status LowCardinality(String),
    started_at DateTime,
    completed_at DateTime,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(started_at)
ORDER BY (user_id, started_at)
SETTINGS index_granularity = 8192;

-- 认知常模表
CREATE TABLE IF NOT EXISTS cognitive_normalize (
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
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (dimension, age_group)
SETTINGS index_granularity = 8192;

-- 添加常模表索引
ALTER TABLE cognitive_normalize ADD INDEX idx_age_dim (age_group, dimension) TYPE minmax GRANULARITY 1;

-- 教育知识表
CREATE TABLE IF NOT EXISTS education_knowledge (
    id UInt64,
    category LowCardinality(String),
    title String,
    content String,
    source String,
    tags Array(String),
    embedding_version Int32,
    version Int32,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (category, created_at)
SETTINGS index_granularity = 8192;

-- 添加教育知识表索引
ALTER TABLE education_knowledge ADD INDEX idx_category (category) TYPE tokenbf_v256 GRANULARITY 1;
ALTER TABLE education_knowledge ADD INDEX idx_tags (tags) TYPE bloom_filter GRANULARITY 1;

-- 常模版本管理表
CREATE TABLE IF NOT EXISTS normalize_version (
    id UInt64,
    version String,
    effective_date Date,
    created_at DateTime DEFAULT now(),
    created_by String,
    change_log String
) ENGINE = MergeTree()
ORDER BY id
SETTINGS index_granularity = 8192;