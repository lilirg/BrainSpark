-- BrainSpark MySQL 数据库初始化
-- 创建 4 个逻辑业务库

-- 用户与合规库
CREATE DATABASE IF NOT EXISTS users_schema CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 测评业务库
CREATE DATABASE IF NOT EXISTS assessment_schema CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 商城与订单库
CREATE DATABASE IF NOT EXISTS mall_schema CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AI 服务库
CREATE DATABASE IF NOT EXISTS ai_schema CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;