-- BrainSpark 初始数据填充

USE users_schema;

-- 初始管理员用户 (密码: admin123, BCrypt hash)
INSERT INTO users (username, password_hash, email, role, status) VALUES
('admin', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'admin@brainspark.com', 'ADMIN', 'ACTIVE');

-- 初始测试教师用户 (密码: teacher123)
INSERT INTO users (username, password_hash, email, role, status, real_name) VALUES
('teacher01', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'teacher01@brainspark.com', 'TEACHER', 'ACTIVE', '张老师'),
('teacher02', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'teacher02@brainspark.com', 'TEACHER', 'ACTIVE', '李老师');

-- 初始测试家长用户 (密码: parent123)
INSERT INTO users (username, password_hash, email, role, status, real_name) VALUES
('parent01', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'parent01@brainspark.com', 'PARENT', 'ACTIVE', '王家长'),
('parent02', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'parent02@brainspark.com', 'PARENT', 'ACTIVE', '刘家长');

USE assessment_schema;

-- 初始班级
INSERT INTO classes (name, grade, teacher_id, description) VALUES
('一年级一班', '一年级', 2, '2026年秋季入学一年级班级'),
('一年级二班', '一年级', 3, '2026年秋季入学一年级班级'),
('二年级一班', '二年级', 2, '2025年秋季入学二年级班级');

-- 初始测评类型
INSERT INTO assessment_types (code, name, description, category, cognitive_dimension, min_age, max_age, duration_seconds, config, is_published, status) VALUES
('SCHULTER', '舒尔特方格', '注意力与反应速度测评，通过点击数字方格测试注意力和反应能力', 'ATTENTION', 'VISUAL', 6, 18, 300, '{"gridSizes": [3, 4, 5], "defaultGridSize": 5, "difficultyLevels": [1, 2, 3]}', TRUE, 'ACTIVE'),
('DIGITAL_SPAN', '数字广度', '工作记忆容量测评，测试短期记忆和数字处理能力', 'MEMORY', 'MEMORY', 6, 18, 300, '{"minSpan": 3, "maxSpan": 9, "defaultSpan": 5, "difficultyLevels": [1, 2, 3]}', TRUE, 'ACTIVE'),
('PATTERN_REASONING', '图形推理', '逻辑推理能力测评，通过图形模式识别测试逻辑思维', 'LOGIC', 'LOGIC', 6, 18, 600, '{"difficultyLevels": [1, 2, 3], "defaultLevel": 2, "questionCount": 20}', TRUE, 'ACTIVE'),
('SPATIAL_ROTATION', '空间旋转', '空间认知能力测评，测试心理旋转和空间想象能力', 'SPATIAL', 'VISUAL', 8, 18, 450, '{"difficultyLevels": [1, 2, 3], "defaultLevel": 2, "rotationAngles": [45, 90, 180]}', TRUE, 'ACTIVE'),
('STROOP_TEST', '斯特鲁普测试', '执行功能测评，测试抑制控制和认知灵活性', 'EXECUTIVE', 'LOGIC', 6, 18, 360, '{"difficultyLevels": [1, 2, 3], "defaultLevel": 2, "trialCount": 60}', TRUE, 'ACTIVE');