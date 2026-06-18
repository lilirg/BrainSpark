-- BrainSpark 测评业务库 - 表结构
-- 基于 docs/architecture/data-model.md 定义

USE assessment_schema;

-- 班级表
CREATE TABLE IF NOT EXISTS classes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    org_id BIGINT,
    name VARCHAR(100) NOT NULL,
    grade VARCHAR(20) NOT NULL,
    description TEXT,
    teacher_id BIGINT,
    max_students INT DEFAULT 50,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_teacher (teacher_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 班级成员表
CREATE TABLE IF NOT EXISTS class_members (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    class_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    role VARCHAR(20),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_class_member (class_id, user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 测评类型表
CREATE TABLE IF NOT EXISTS assessment_types (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category ENUM('ATTENTION', 'MEMORY', 'LOGIC', 'SPATIAL', 'LANGUAGE', 'EXECUTIVE') NOT NULL,
    cognitive_dimension VARCHAR(50),
    min_age INT NOT NULL,
    max_age INT NOT NULL,
    duration_seconds INT NOT NULL,
    version VARCHAR(20),
    config JSON,
    is_published BOOLEAN DEFAULT FALSE,
    status ENUM('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 测评任务表
CREATE TABLE IF NOT EXISTS assessment_tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    org_id BIGINT,
    class_id BIGINT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    type_code VARCHAR(50) NOT NULL,
    config JSON,
    difficulty INT DEFAULT 1,
    duration_min INT DEFAULT 10,
    assigned_at TIMESTAMP NULL,
    start_at TIMESTAMP NULL,
    end_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    status ENUM('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED') NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_type (type_code),
    INDEX idx_class (class_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 任务分发表
CREATE TABLE IF NOT EXISTS task_assignments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_code VARCHAR(32) NOT NULL,
    class_room_code VARCHAR(20),
    due_date DATE NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_classroom (class_room_code, due_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 学生任务分发表
CREATE TABLE IF NOT EXISTS student_task_assignments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    assignment_id BIGINT NOT NULL,
    student_id BIGINT NOT NULL,
    status ENUM('PENDING', 'IN_PROGRESS', 'COMPLETED', 'EXPIRED') NOT NULL DEFAULT 'PENDING',
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    INDEX idx_student_status (student_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 测评会话表
CREATE TABLE IF NOT EXISTS assessment_sessions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id CHAR(36) NOT NULL UNIQUE,
    task_code VARCHAR(32) NOT NULL,
    student_id BIGINT NOT NULL,
    type_id BIGINT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NULL,
    total_time_sec FLOAT,
    grid_size TINYINT,
    is_completed TINYINT DEFAULT 0,
    status ENUM('PENDING', 'IN_PROGRESS', 'PAUSED', 'COMPLETED', 'ABANDONED') NOT NULL DEFAULT 'PENDING',
    device_info JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_student_task (student_id, task_code),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 事件汇总表
CREATE TABLE IF NOT EXISTS event_summaries (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id CHAR(36) NOT NULL,
    event_type VARCHAR(20),
    grid_cell TINYINT,
    reaction_time_ms SMALLINT,
    is_correct TINYINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 测评结果表
CREATE TABLE IF NOT EXISTS assessment_results (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    task_id BIGINT,
    type_code VARCHAR(50) NOT NULL,
    request_id VARCHAR(100),
    session_id VARCHAR(100),
    score_data JSON,
    cognitive_profile JSON,
    ai_recommendations JSON,
    report_status ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED') NOT NULL DEFAULT 'PENDING',
    status ENUM('FINISHED', 'PROCESSING', 'FAILED') NOT NULL DEFAULT 'FINISHED',
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_task (task_id),
    INDEX idx_status (report_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 测评结果表 v2
CREATE TABLE IF NOT EXISTS assessment_results_v2 (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id CHAR(36) NOT NULL UNIQUE,
    type_code VARCHAR(32),
    target_age_group VARCHAR(20),
    avg_reaction_time_ms SMALLINT,
    correct_count TINYINT,
    total_clicks TINYINT,
    validity_status ENUM('VALID', 'FLAGGED', 'INVALID'),
    report_generated TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;