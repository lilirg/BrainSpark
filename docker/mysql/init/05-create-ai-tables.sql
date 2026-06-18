-- BrainSpark AI 服务库 - 表结构
-- 基于 docs/architecture/data-model.md 定义

USE ai_schema;

-- 知识库表
CREATE TABLE IF NOT EXISTS knowledge_base (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    doc_id VARCHAR(64) NOT NULL UNIQUE,
    doc_title VARCHAR(200),
    category VARCHAR(50),
    tags JSON,
    embedding_dim TINYINT DEFAULT 1536,
    version INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 报告表
CREATE TABLE IF NOT EXISTS reports (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    result_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    report_type VARCHAR(32),
    report_json LONGTEXT,
    version INT DEFAULT 1,
    is_official TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_result (result_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;