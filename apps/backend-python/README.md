# BrainSpark 业务后端服务 (Python FastAPI)

> 从 Java Spring Boot 3 迁移至 Python FastAPI

## 技术栈

- **框架**: FastAPI 0.109+
- **ORM**: SQLAlchemy 2.0 (异步)
- **数据库**: MySQL 8.0 / MongoDB / ClickHouse / Redis
- **认证**: JWT (python-jose) + bcrypt
- **迁移**: Alembic
- **测试**: pytest + pytest-asyncio
- **部署**: Docker + Uvicorn

## 快速开始

### 环境要求

- Python 3.11+
- Poetry 1.7+
- MySQL 8.0+

### 安装

```bash
# 克隆项目后
cd apps/backend-python

# 复制环境变量配置
cp .env.example .env

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell
```

### 运行

```bash
# 开发模式（热重载）
uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
```

### 数据库迁移

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "init"

# 执行迁移
alembic upgrade head
```

### 测试

```bash
pytest -v
```

## 项目结构

```
apps/backend-python/
├── main.py                  # 应用入口
├── pyproject.toml           # 项目配置与依赖
├── alembic.ini              # 数据库迁移配置
├── Dockerfile               # Docker 镜像
├── .env.example             # 环境变量示例
├── app/
│   ├── __init__.py
│   ├── core/                # 核心模块
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库连接
│   │   ├── exceptions.py    # 异常定义
│   │   ├── logging.py       # 日志配置
│   │   └── response.py      # 统一响应格式
│   ├── models/              # SQLAlchemy 数据模型
│   │   ├── user.py          # 用户模型
│   │   └── ...
│   ├── schemas/             # Pydantic 校验模型
│   │   ├── user.py          # 用户相关
│   │   └── ...
│   ├── services/            # 业务逻辑层
│   │   ├── user_service.py  # 用户服务
│   │   ├── auth_service.py  # 认证服务
│   │   └── ...
│   ├── routers/             # API 路由
│   │   ├── users.py         # 用户管理
│   │   ├── auth.py          # 认证
│   │   └── ...
│   └── middleware/          # 中间件
│       ├── cors.py          # CORS
│       ├── request_id.py    # 请求追踪
│       └── error_handler.py # 异常处理
├── alembic/                 # 数据库迁移
│   ├── env.py
│   └── versions/
└── tests/                   # 测试
    └── test_health.py
```

## API 文档

- 开发环境: http://localhost:8080/docs (Swagger UI)
- 开发环境: http://localhost:8080/redoc (ReDoc)

## 与 Java 版本的差异

| 特性 | Java (Spring Boot 3) | Python (FastAPI) |
|------|---------------------|-------------------|
| 启动类 | BrainSparkApplication.java | main.py |
| 控制器 | UserController.java | routers/users.py |
| 服务 | UserService.java | services/user_service.py |
| 实体 | User.java (JPA) | models/user.py (SQLAlchemy) |
| 仓库 | UserRepository.java (JPA) | 直接使用 SQLAlchemy Session |
| 配置 | application.yml | config.py + .env |
| 构建 | Maven (pom.xml) | Poetry (pyproject.toml) |