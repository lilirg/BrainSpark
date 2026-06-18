-- BrainSpark 用户与合规库 - 表结构
-- 基于 docs/architecture/data-model.md 定义

USE users_schema;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    role ENUM('ADMIN', 'MANAGER', 'EMPLOYEE', 'TEACHER', 'PARENT', 'STUDENT') NOT NULL,
    real_name VARCHAR(50),
    avatar VARCHAR(255),
    status ENUM('ACTIVE', 'INACTIVE', 'LOCKED', 'DISABLED', 'PENDING_VERIFY') NOT NULL DEFAULT 'ACTIVE',
    extra_info JSON,
    last_login_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_role (role),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 学生信息表 (在 users_schema 中存储学生扩展信息)
CREATE TABLE IF NOT EXISTS students (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    student_code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    name_hash VARCHAR(64) NOT NULL UNIQUE,
    gender ENUM('MALE', 'FEMALE', 'OTHER') NOT NULL,
    age INT NOT NULL,
    birth_year YEAR,
    grade VARCHAR(20) NOT NULL,
    class_id BIGINT,
    parent_id BIGINT,
    school_name VARCHAR(128),
    parent_guardian_name VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_class (class_id),
    INDEX idx_parent (parent_id),
    INDEX idx_student_code (student_code),
    INDEX idx_birth_year (birth_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 家庭绑定表
CREATE TABLE IF NOT EXISTS family_bindings (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    parent_user_id BIGINT NOT NULL,
    student_user_id BIGINT NOT NULL,
    relationship ENUM('FATHER', 'MOTHER', 'GUARDIAN', 'OTHER') NOT NULL,
    status ENUM('PENDING', 'ACTIVE', 'REVOKED') NOT NULL DEFAULT 'PENDING',
    binding_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_parent_student (parent_user_id, student_user_id),
    INDEX idx_parent (parent_user_id),
    INDEX idx_student (student_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 监护人同意表
CREATE TABLE IF NOT EXISTS guardian_consent (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    guardian_user_id BIGINT NOT NULL,
    child_user_id BIGINT NOT NULL,
    consent_type ENUM('DATA_COLLECTION', 'ASSESSMENT', 'SHARING') NOT NULL,
    consent_given TINYINT DEFAULT 0,
    status ENUM('PENDING', 'GRANTED', 'REVOKED') NOT NULL DEFAULT 'PENDING',
    consent_method VARCHAR(20),
    consent_proof VARCHAR(255),
    consented_at TIMESTAMP NULL,
    is_active TINYINT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_guardian_child (guardian_user_id, child_user_id),
    INDEX idx_consent_given (consent_given)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;