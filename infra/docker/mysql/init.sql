-- BrainSpark MySQL 数据库初始化脚本
-- 开发环境使用

-- 创建业务数据库
CREATE DATABASE IF NOT EXISTS `users_schema` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS `assessment_schema` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS `mall_schema` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS `ai_schema` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（如果使用非 root 用户）
-- CREATE USER IF NOT EXISTS 'brainspark'@'%' IDENTIFIED BY 'brainspark_dev';
-- GRANT ALL PRIVILEGES ON `users_schema`.* TO 'brainspark'@'%';
-- GRANT ALL PRIVILEGES ON `assessment_schema`.* TO 'brainspark'@'%';
-- GRANT ALL PRIVILEGES ON `mall_schema`.* TO 'brainspark'@'%';
-- GRANT ALL PRIVILEGES ON `ai_schema`.* TO 'brainspark'@'%';
-- FLUSH PRIVILEGES;

-- 使用 root 用户，直接使用默认的 brainspark 数据库
USE `brainspark`;

-- 用户表
CREATE TABLE IF NOT EXISTS `users` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
    `role` VARCHAR(20) NOT NULL DEFAULT 'student' COMMENT '角色: student/parent/teacher/admin',
    `real_name` VARCHAR(100) DEFAULT NULL COMMENT '真实姓名',
    `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    `avatar_url` VARCHAR(500) DEFAULT NULL COMMENT '头像URL',
    `extra_info` JSON DEFAULT NULL COMMENT '扩展信息',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    KEY `idx_role` (`role`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 班级表
CREATE TABLE IF NOT EXISTS `classes` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '班级ID',
    `name` VARCHAR(100) NOT NULL COMMENT '班级名称',
    `grade` VARCHAR(20) DEFAULT NULL COMMENT '年级',
    `org_id` BIGINT DEFAULT NULL COMMENT '所属机构ID',
    `description` VARCHAR(500) DEFAULT NULL COMMENT '班级描述',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_org_id` (`org_id`),
    KEY `idx_grade` (`grade`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='班级表';

-- 班级成员表
CREATE TABLE IF NOT EXISTS `class_members` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `class_id` BIGINT NOT NULL COMMENT '班级ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `role` VARCHAR(20) NOT NULL DEFAULT 'student' COMMENT '角色: student/teacher',
    `joined_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_class_user` (`class_id`, `user_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='班级成员表';

-- 学生信息表
CREATE TABLE IF NOT EXISTS `student_profiles` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `name_hash` VARCHAR(64) DEFAULT NULL COMMENT '姓名哈希',
    `birth_year` YEAR DEFAULT NULL COMMENT '出生年份',
    `gender` VARCHAR(10) DEFAULT NULL COMMENT '性别',
    `classroom_code` VARCHAR(50) DEFAULT NULL COMMENT '教室代码',
    `extra_info` JSON DEFAULT NULL COMMENT '扩展信息',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_id` (`user_id`),
    KEY `idx_classroom_code` (`classroom_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生信息表';

-- 测评类型表
CREATE TABLE IF NOT EXISTS `assessment_types` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `code` VARCHAR(50) NOT NULL COMMENT '类型编码',
    `name` VARCHAR(100) NOT NULL COMMENT '类型名称',
    `description` TEXT DEFAULT NULL COMMENT '描述',
    `cognitive_dimension` VARCHAR(50) DEFAULT NULL COMMENT '认知维度',
    `config_template` JSON DEFAULT NULL COMMENT '配置模板',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测评类型表';

-- 测评任务表
CREATE TABLE IF NOT EXISTS `assessment_tasks` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `type_code` VARCHAR(50) NOT NULL COMMENT '测评类型编码',
    `name` VARCHAR(200) NOT NULL COMMENT '任务名称',
    `config` JSON DEFAULT NULL COMMENT '任务配置',
    `difficulty` INT DEFAULT 1 COMMENT '难度等级',
    `duration_minutes` INT DEFAULT NULL COMMENT '预计时长(分钟)',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_type_code` (`type_code`),
    KEY `idx_difficulty` (`difficulty`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测评任务表';

-- 测评结果表
CREATE TABLE IF NOT EXISTS `assessment_results` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `task_id` BIGINT NOT NULL COMMENT '任务ID',
    `session_id` VARCHAR(100) DEFAULT NULL COMMENT '会话ID',
    `score_data` JSON DEFAULT NULL COMMENT '得分数据',
    `cognitive_profile` JSON DEFAULT NULL COMMENT '认知画像',
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态: pending/completed/analyzed',
    `started_at` DATETIME DEFAULT NULL COMMENT '开始时间',
    `completed_at` DATETIME DEFAULT NULL COMMENT '完成时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_task_id` (`task_id`),
    KEY `idx_status` (`status`),
    KEY `idx_completed_at` (`completed_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测评结果表';

-- 插入默认测评类型
INSERT INTO `assessment_types` (`code`, `name`, `description`, `cognitive_dimension`, `config_template`) VALUES
('VISUAL_ATTENTION', '视觉注意力', '评估视觉注意力的广度、稳定性和分配能力', 'attention', '{"grid_size": 5, "trial_count": 20, "stimulus_duration_ms": 300}'),
('WORKING_MEMORY', '工作记忆', '评估工作记忆的容量和更新能力', 'memory', '{"span_range": "3-8", "trial_count": 15, "delay_ms": 2000}'),
('EXECUTIVE_FUNCTION', '执行功能', '评估抑制控制、认知灵活性和计划能力', 'executive', '{"condition_count": 3, "trial_count": 30, "switch_ratio": 0.25}')
ON DUPLICATE KEY UPDATE `name` = VALUES(`name`);