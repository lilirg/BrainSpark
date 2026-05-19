import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # AI Models
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4o")
    
    # Vector DB
    MILVUS_URI: str = os.getenv("MILVUS_URI", "http://localhost:19530")
    MILVUS_COLLECTION: str = os.getenv("MILVUS_COLLECTION", "education_knowledge")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/brainspark")
    
    # API
    APP_NAME: str = "BrainSpark AI Service"
    VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()