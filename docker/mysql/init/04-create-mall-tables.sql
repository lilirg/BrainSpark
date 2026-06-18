-- BrainSpark 商城与订单库 - 表结构
-- 基于 docs/architecture/data-model.md 定义

USE mall_schema;

-- 商品表
CREATE TABLE IF NOT EXISTS products (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sku_code VARCHAR(32) NOT NULL UNIQUE,
    name VARCHAR(128) NOT NULL,
    description TEXT,
    price_cents INT NOT NULL,
    currency CHAR(3) DEFAULT 'CNY',
    stripe_price_id VARCHAR(128),
    wechat_pay_product_id VARCHAR(128),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(32) NOT NULL UNIQUE,
    user_id BIGINT NOT NULL,
    student_id BIGINT,
    product_sku VARCHAR(32) NOT NULL,
    amount_cents INT NOT NULL,
    status ENUM('PENDING_PAYMENT', 'PENDING', 'PAID', 'COMPLETED', 'REFUNDED', 'CANCELLED') NOT NULL DEFAULT 'PENDING_PAYMENT',
    payment_channel VARCHAR(20),
    payment_intent_id VARCHAR(128),
    paid_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_order_no (order_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 订阅方案表
CREATE TABLE IF NOT EXISTS subscription_plans (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    plan_type VARCHAR(32) NOT NULL,
    price_cents INT NOT NULL,
    stripe_price_id VARCHAR(128),
    status TINYINT DEFAULT 1,
    expires_at_offset_days INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;