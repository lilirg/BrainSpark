"""应用配置模块 - 通过环境变量加载配置"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # 应用基础配置
    APP_NAME: str = "BrainSpark Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENV: Literal["dev", "staging", "prod"] = "dev"

    # 服务端口
    HOST: str = "0.0.0.0"
    PORT: int = 8080

    # MySQL 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "brainspark"
    DB_PASSWORD: str = ""
    DB_NAME: str = "brainspark"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    @property
    def database_url(self) -> str:
        """获取 MySQL 异步连接 URL"""
        return (
            f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    # MongoDB 配置
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "brainspark"

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # ClickHouse 配置
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 9000
    CLICKHOUSE_DB: str = "brainspark"

    # JWT 配置
    JWT_SECRET_KEY: str = ""  # 必须通过环境变量设置，禁止使用默认值
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120  # 2小时
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 密码哈希
    PASSWORD_HASH_ALGORITHM: str = "bcrypt"

    # AI 服务配置
    AI_SERVICE_URL: str = "http://localhost:8001"
    AI_SERVICE_TIMEOUT: int = 60

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"

    # CORS 配置
    # 生产环境必须通过环境变量 CORS_ORIGINS 设置具体域名，禁止使用通配符
    # 格式：逗号分隔的域名列表，例如 "https://admin.brainspark.com,https://app.brainspark.com"
    CORS_ORIGINS: str = ""
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # 分页默认值
    PAGE_DEFAULT_SIZE: int = 20
    PAGE_MAX_SIZE: int = 100

    # 功能开关
    ENABLE_TODAY_TASKS: bool = False

    def validate(self) -> None:
        """验证配置项（在应用启动时调用，而非模块导入时）
        
        在 main.py 的 lifespan 启动事件中调用此方法，
        避免因 .env 文件缺失导致应用导入时崩溃。
        """
        if not self.JWT_SECRET_KEY:
            raise ValueError(
                "JWT_SECRET_KEY 未设置。请在 .env 文件中添加 "
                "JWT_SECRET_KEY=<随机密钥>，或通过环境变量注入。"
            )
        if self.JWT_SECRET_KEY == "your-secret-key-change-in-production":
            raise ValueError(
                "JWT_SECRET_KEY 使用了不安全的默认值，请生成随机密钥"
            )
        if self.ENV == "prod" and not self.DB_PASSWORD:
            raise ValueError("生产环境必须通过环境变量设置 DB_PASSWORD")

    @property
    def cors_origins(self) -> list[str]:
        """根据环境动态返回 CORS 允许的源

        优先使用环境变量 CORS_ORIGINS 配置的域名列表，
        未配置时根据环境返回默认值。
        注意：allow_origins=["*"] 与 allow_credentials=True 不兼容。
        """
        if self.CORS_ORIGINS:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        # 未配置时，根据环境返回默认值
        if self.ENV == "prod":
            raise ValueError(
                "生产环境必须通过 CORS_ORIGINS 环境变量配置允许的域名，"
                "例如：CORS_ORIGINS=https://admin.brainspark.com,https://app.brainspark.com"
            )
        return [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
        ]


settings = Settings()