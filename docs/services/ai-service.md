# BrainSpark AI 服务设计文档

> 本文档详细描述 BrainSpark 平台的 AI 服务 (`ai-service`) 的架构与设计。该服务基于 Python FastAPI 构建，负责认知能力分析、AI 报告生成和教育知识库检索。

## 1. 架构概述

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Gateway Layer                                │
│  ┌─────────────────────┐    ┌───────────────────────────────────┐   │
│  │  Go API Gateway     │    │  Go WebSocket Gateway             │   │
│  └─────────────────────┘    └───────────────────────────────────┘   │
└───────────────┬──────────────────────────────┬──────────────────────┘
                │                              │
                ▼                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Service Layer                                   │
│  ┌─────────────────────┐    ┌───────────────────────────────────┐   │
│  │  Java Backend       │    │  Python AI Service                │   │
│  │  (port 8080)         │    │  (port 8001)                      │   │
│  │                     │    │                                   │   │
│  │  - 用户服务         │    │  - 认知维度分析                   │   │
│  │  - 测评服务         │    │  - AI 报告生成                    │   │
│  │  - 报告服务         │    │  - 教育知识检索 (RAG)             │   │
│  │                     │    │  - 训练计划推荐                   │   │
│  └─────────────────────┘    └───────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Data Layer                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Milvus  │  │  Redis   │  │  MinIO   │  │  LLM API │           │
│  │ 向量库   │  │ 缓存    │  │ 文件存储 │  │ OpenAI   │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. 目录结构

```
apps/ai-service/
├── main.py                                  # 入口文件
├── requirements.txt                         # Python 依赖
└── app/
    ├── __init__.py
    ├── core/                                # 核心配置
    │   └── config.py                        # 环境变量配置
    ├── analysis/                            # 认知分析模块
    │   └── analyzer.py                      # 认知分析器
    ├── rag/                                 # RAG 模块
    │   └── vector_store.py                  # Milvus 向量存储（单例模式）
    └── schemas/                             # Pydantic 模型
        ├── __init__.py
        ├── assessment.py                    # 测评请求/响应
        └── report.py                        # 报告请求/响应
```

## 3. 数据库设计

### 3.1 Milvus 集合设计

```python
# rag/collection_definitions.py
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

# 教育知识集合
KNOWLEDGE_SCHEMA = CollectionSchema([
    FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=50),  # 类别
    FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=200),
    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=200),   # 来源
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),  # 向量维度
    FieldSchema(name="version", dtype=DataType.INT64),                      # 版本
], description="教育知识集合")

# 测评常模集合
NORMALIZE_SCHEMA = CollectionSchema([
    FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
    FieldSchema(name="age_group", dtype=DataType.VARCHAR, max_length=20),  # 年龄分组
    FieldSchema(name="dimension", dtype=DataType.VARCHAR, max_length=50),  # 维度
    FieldSchema(name="mean", dtype=DataType.FLOAT),                         # 均值
    FieldSchema(name="std", dtype=DataType.FLOAT),                          # 标准差
    FieldSchema(name="p50", dtype=DataType.FLOAT),                          # P50 百分位
    FieldSchema(name="p84", dtype=DataType.FLOAT),                          # P84 百分位
    FieldSchema(name="p95", dtype=DataType.FLOAT),                          # P95 百分位
    FieldSchema(name="gender", dtype=DataType.VARCHAR, max_length=10),      # 性别
    FieldSchema(name="sample_size", dtype=DataType.INT64),                  # 样本量
], description="测评常模集合")
```

### 3.2 Milvus 索引配置

```python
# rag/index_config.py
from pymilvus import utility

# 向量索引（IVF_FLAT）
INDEX_PARAMS = {
    "metric_type": "IP",  # 余弦相似度
    "index_type": "IVF_FLAT",
    "params": {"nlist": 2048}
}

# 标量字段索引
SCALAR_INDEXES = [
    {"field_name": "category", "index_type": "STANDARD"},
    {"field_name": "version", "index_type": "STANDARD"},
]
```

## 4. 服务架构

### 4.1 认知分析服务

```
测评事件数据 (Go 网关 → Kafka → 后端)
  │
  ▼
事件预处理 & 校验
  │
  ▼
特征提取 (反应时/正确率/轨迹)
  │
  ▼
认知维度计算 (记忆/注意/逻辑/创造/观察/想象)
  │
  ▼
常模对比 (Milvus 查询 → 百分位)
  │
  ▼
结果返回 & AI 建议生成
```

```python
# services/cognitive_analyzer.py
import math
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class DimensionAnalysis(BaseModel):
    dimension: str
    score: float = Field(..., ge=0, le=100)
    percentile: float = Field(..., ge=0, le=100, description="百分位")
    level: str  # 优秀/良好/中等/待提升
    raw_metrics: Dict[str, float] = {}
    
class CognitiveProfile(BaseModel):
    student_id: str
    session_id: str
    assessment_type: str
    dimensions: List[DimensionAnalysis]
    overall_score: float
    analysis_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def top_dimension(self) -> str:
        return max(self.dimensions, key=lambda d: d.score).dimension
    
    @property
    def need_attention_dims(self) -> List[str]:
        return [d.dimension for d in self.dimensions if d.score < 60]
```

#### 4.1.1 特征提取

```python
class FeatureExtractor:
    """从测评事件中提取认知特征"""
    
    def __init__(self):
        self.dimensions = {
            "记忆": ["RECALL", "MATCH", "SEQUENCE"],
            "注意": ["FOCUS", "DIVIDE", "SUSTAIN"],
            "逻辑": ["RULE", "HYPOTHESIS", "PATTERN"],
            "创造": ["OPEN_END", "MULTI_SOLUTION"],
            "观察": ["DETAIL", "DIFFERENCE"],
            "想象": ["SPATIAL", "TRANSFORMATION"],
        }
        
    def extract(self, events: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        将原始事件按维度分类并提取关键指标
        """
        features = {}
        
        for event in events:
            dim = event.get("dimension", "UNKNOWN")
            metric = {
                "timestamp": event.get("performance_start"),
                "duration_ms": event.get("reaction_time"),
                "correct": event.get("is_correct"),
                "x": event.get("pointer_x"),
                "y": event.get("pointer_y"),
                "path_length": event.get("path_length"),
            }
            
            if dim not in features:
                features[dim] = []
            features[dim].append(metric)
            
        return features
```

#### 4.1.2 评分计算

```python
class ScoreCalculator:
    """计算各维度得分"""
    
    # 年龄分组基准反应时 (ms)
    AGE_REACTION_BASELINES = {
        "6-8": 800,
        "9-11": 650,
        "12-14": 550,
        "15-17": 500,
    }
    
    def calculate_score(self, metrics: List[Dict], 
                        age_group: str) -> float:
        """
        基于反应时、正确率和路径效率计算维度得分
        """
        # 1. 计算平均反应时
        reaction_times = [m["duration_ms"] for m in metrics if m["duration_ms"]]
        if not reaction_times:
            return 0.0
            
        avg_rt = sum(reaction_times) / len(reaction_times)
        
        # 2. 基准对比 (越低越好)
        baseline = self.AGE_REACTION_BASELINES.get(age_group, 650)
        rt_score = max(0, min(100, 100 - (avg_rt - baseline) / baseline * 100))
        
        # 3. 正确率
        correct_count = sum(1 for m in metrics if m["correct"])
        accuracy = correct_count / len(metrics) * 100
        
        # 4. 加权总分
        total_score = rt_score * 0.4 + accuracy * 0.6
        
        # 5. 标准化到 0-100
        return min(100, max(0, total_score))
    
    def to_percentile(self, score: float, age_group: str, 
                      dimension: str) -> float:
        """
        使用常模数据将原始分数转换为百分位
        """
        # 查询 Milvus 常模数据
        normalize_data = self.get_normalize_data(age_group, dimension)
        if not normalize_data:
            return 50.0  # 默认中位数
            
        # Z-Score 计算百分位
        z_score = (score - normalize_data["mean"]) / normalize_data["std"]
        percentile = self._z_to_percentile(z_score)
        
        return percentile
    
    def _z_to_percentile(self, z: float) -> float:
        """Z-Score 转百分位 (正态分布)"""
        return 0.5 * (1 + self._erf(z / math.sqrt(2)))
    
    def _erf(self, x: float) -> float:
        """误差函数近似"""
        t = 1.0 / (1.0 + 0.3275911 * abs(x))
        a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
        return 1 - ((((a5*t + a4)*t + a3)*t + a2)*t + a1)*t * math.exp(-x*x)
```

### 4.2 报告生成服务

#### 4.2.1 RAG 流程

```
用户请求生成报告
  │
  ▼
1. 提取测评数据摘要 (脱敏)
  │
  ▼
2. 查询教育知识库 (相似性检索)
  │
  ▼
3. 多路检索 (向量 + 标量 + 图谱)
  │
  ▼
4. 重排序 (Cross-Encoder)
  │
  ▼
5. Prompt 组装
  │
  ▼
6. LLM 生成报告
  │
  ▼
7. 安全合规过滤
  │
  ▼
8. 返回报告
```

```python
# services/report_generator.py
import json
from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from app.schemas.report import ReportRequest, ReportResponse
from app.prompts.report_prompt import REPORT_TEMPLATE
from app.rag.retriever import RAGRetriever
from app.services.compliance_service import sanitize_for_llm
from app.services.llm_service import LLMService

class ReportGenerator:
    """AI 报告生成器"""
    
    def __init__(self, llm_service: LLMService, retriever: RAGRetriever):
        self.llm = llm_service.get_llm()
        self.retriever = retriever
        self.prompt = PromptTemplate(
            input_variables=["profile", "knowledge"],
            template=REPORT_TEMPLATE
        )
        
    async def generate(self, request: ReportRequest, 
                       cognitive_profile: CognitiveProfile) -> str:
        """生成完整的认知评估报告"""
        
        # 1. 合规脱敏
        safe_profile = sanitize_for_llm(cognitive_profile)
        student_info = safe_profile.get("student_info", {})
        anonymized_name = f"学生{student_info.get('id', '???')[-4:]}"
        
        # 2. RAG 检索相关教育知识
        query = f"认知评分{anonymized_name}: {self._build_query(safe_profile)}"
        relevant_knowledge = await self.retriever.search(
            query=query,
            k=5,
            filters={"category": ["注意力训练", "记忆力提升", "逻辑思维"]}
        )
        
        # 3. Prompt 组装
        knowledge_context = json.dumps([
            {"title": doc["title"], "content": doc["content"]}
            for doc in relevant_knowledge
        ], ensure_ascii=False)
        
        # 4. 生成报告
        chain = LLMChain(llm=self.llm, prompt=self.prompt)
        report = await chain.arun(
            profile=json.dumps(safe_profile, ensure_ascii=False),
            knowledge=knowledge_context
        )
        
        # 5. 安全过滤
        report = self._apply_safety_filters(report)
        
        return report
    
    def _build_query(self, profile: Dict[str, Any]) -> str:
        """构建查询词"""
        dims = profile.get("dimensions", [])
        low_dims = [d["name"] for d in dims if d["score"] < 60]
        high_dims = [d["name"] for d in dims if d["score"] > 80]
        
        parts = []
        if low_dims:
            parts.append(f"低分维度: {', '.join(low_dims)}")
        if high_dims:
            parts.append(f"高分维度: {', '.join(high_dims)}")
            
        return " ".join(parts)
    
    def _apply_safety_filters(self, report: str) -> str:
        """安全过滤"""
        # 1. 添加 AI 声明
        ai_disclaimer = "\n\n---\n⚠️ 本报告由 AI 辅助生成，仅供参考，不构成医疗或教育诊断结论。\n"
        
        # 2. 检查敏感词
        blocked_phrases = ["智商低下", "自闭症", "多动症", "ADHD"]
        for phrase in blocked_phrases:
            report = report.replace(phrase, "")
            
        return report + ai_disclaimer
```

#### 4.2.2 提示词模板

```python
# prompts/report_prompt.py
REPORT_TEMPLATE = """你是一位资深儿童心理教育学专家。请根据以下评估数据，为 {student_info} 生成一份详细的认知能力评估报告。

## 用户基本信息
- 年龄: {age}
- 年级: {grade}
- 性别: {gender}

## 认知评估结果
```json
{profile}
```

## 相关知识参考
{knowledge}

## 报告格式要求

### 一、综合评估
简要概括 {anonymized_name} 的整体认知能力表现，突出亮点。

### 二、维度分析
逐项分析六大认知维度（注意力、记忆力、逻辑、创造、观察、想象）：
- 该维度的定义和在学龄儿童学习中的作用
- {anonymized_name} 在此维度的表现
- 与同龄人相比的大致位置

### 三、学习场景映射
将该学生的认知特征映射到具体学习场景：
- 阅读：推荐阅读策略
- 数学：推荐思维方式
- 课堂专注：推荐方法

### 四、训练建议
基于最低的两项能力维度，推荐2-3个针对性训练方案。

### 五、家长指导
给家长的实用建议和注意事项。

要求：
1. 语气温暖、正面，避免评判性语言
2. 使用具体示例而非抽象描述
3. 所有建议必须有科学依据或可执行性
4. 严禁诊断性语言（如"患有ADHD"等）
5. 适当鼓励，激发信心
6. 字数: 800-1500字
"""
```

### 4.3 训练推荐服务

```python
# services/training_recommender.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from enum import Enum

class TrainingType(str, Enum):
    DIGITAL = "数字训练"       # App 内训练
    PHYSICAL = "体感训练"      # 户外/体感活动
    PRACTICE = "日常练习"      # 学习习惯改进

class TrainingExercise(BaseModel):
    id: str
    name: str
    type: TrainingType
    duration_min: int
    difficulty: int = Field(ge=1, le=5)
    description: str
    expected_benefit: str
    
class TrainingPlan(BaseModel):
    plan_id: str
    student_id: str
    objectives: List[str]
    exercises: List[TrainingExercise]
    weekly_schedule: Dict[str, List[str]]  # Monday-Friday schedule
    duration_weeks: int = 4
    preview_week: int = 1
    generated_at: str
    ai_model_version: str = "v1.0"
```

```python
class TrainingRecommender:
    """训练计划推荐服务"""
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service.get_llm()
        
    async def generate_plan(self, cognitive_profile: CognitiveProfile,
                           user_preferences: Dict[str, Any]) -> TrainingPlan:
        """基于认知评估生成训练计划"""
        
        # 1. 分析需求
        needs = self._analyze_needs(cognitive_profile)
        
        # 2. 检索可训练内容
        exercises = self._recommend_exercises(needs, user_preferences)
        
        # 3. LLM 优化周计划
        schedule = await self._optimize_schedule(exercises, needs)
        
        return TrainingPlan(
            plan_id=f"plan-{cognitive_profile.student_id}-{int(time.time())}",
            student_id=cognitive_profile.student_id,
            objectives=self._build_objectives(needs),
            exercises=exercises,
            weekly_schedule=schedule
        )
    
    def _analyze_needs(self, profile: CognitiveProfile) -> List[Dict[str, Any]]:
        """分析训练需求"""
        sorted_dims = sorted(profile.dimensions, key=lambda d: d.score)
        
        needs = []
        for dim in sorted_dims[:2]:  # 最低的维度优先
            needs.append({
                "dimension": dim.dimension,
                "current_score": dim.score,
                "goal": f"将{dim.dimension}能力提升至75分以上",
                "priority": "high" if dim.score < 50 else "medium"
            })
        return needs
```

### 4.4 向量检索服务

```python
# rag/vector_store.py
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType
from langchain.embeddings import OpenAIEmbeddings
from app.core.config import settings

class MilvusVectorStore:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._connect()
        self._embeddings = OpenAIEmbeddings()
    
    def _connect(self):
        connections.connect(
            alias="default",
            uri=settings.MILVUS_URI
        )
    
    def get_collection(self) -> Collection:
        return Collection(settings.MILVUS_COLLECTION)
    
    async def add_documents(self, documents: list[dict]) -> list[str]:
        """添加文档到向量数据库"""
        ids = []
        for doc in documents:
            embedding = await self._embeddings.aembed_query(doc["content"])
            ids.append(doc["id"])
        return ids
    
    async def similarity_search(self, query: str, k: int = 5) -> list[dict]:
        """相似性搜索"""
        query_embedding = await self._embeddings.aembed_query(query)
        # 简化实现，实际应使用 Milvus search API
        return []
    
    async def search_by_id(self, doc_id: str) -> dict | None:
        """通过ID搜索文档"""
        return None
```

## 5. 安全与合规

### 5.1 隐私脱敏

```python
# services/compliance_service.py
class ComplianceService:
    """合规脱敏服务"""
    
    SENSITIVE_FIELDS = {
        "school", "address", "phone", "id_card", "hospital"
    }
    
    @staticmethod
    def sanitize(user_data: Dict) -> Dict:
        """脱敏用户数据"""
        sanitized = {}
        for key, value in user_data.items():
            if key in ComplianceService.SENSITIVE_FIELDS:
                sanitized[key] = "******"
            elif key == "name":
                sanitized[key] = ComplianceService._mask_name(value)
            else:
                sanitized[key] = value
        return sanitized
    
    @staticmethod
    def _mask_name(name: str) -> str:
        """姓名脱敏"""
        if not name or len(name) < 2:
            return name
        return name[0] + "*" * (len(name) - 1)
    
    @staticmethod
    async def verify_content(report: str) -> bool:
        """验证生成内容是否合规"""
        blocked_words = ["天赋", "天才", "最强大脑", "治愈"]
        return not any(word in report for word in blocked_words)
```

### 5.2 内容安全

```python
# prompts/safety_prompt.py
SAFETY_CHECK_PROMPT = """你是一位儿童内容安全审核员。请检查以下报告是否存在以下问题：

禁止内容：
1. 诊断性用语（如"患有XXX症"）
2. 负面标签（如"低智商"、"有问题"）
3. 绝对化用语（如"最"、"天才"）
4. 医疗建议（如"需要吃药"、"必须手术"）

如果报告包含上述内容，请修改为适当措辞。
否则，直接返回原文并标记 safe=true。

报告内容:
{report}
"""
```

## 6. 接口设计

### 6.1 核心 API

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/v1/assessments/analyze` | 分析测评结果 | JWT |
| `POST` | `/api/v1/reports/generate` | 生成报告 | JWT |
| `POST` | `/api/v1/knowledge/index` | 索引知识到 Milvus | Admin |
| `GET` | `/api/v1/health` | 健康检查 | 无 |

### 6.2 认知分析 API

#### 请求

```json
// POST /api/v1/assessments/analyze
{
    "student_id": "stu_12345",
    "session_id": "session_67890",
    "assessment_type": "schelter_grid",
    "student_info": {
        "age": 10,
        "grade": "5年级",
        "gender": "男"
    },
    "events": [
        {
            "type": "CLICK",
            "target_id": 5,
            "reaction_time_ms": 450,
            "is_correct": true,
            "timestamp": 1234.567,
            "pointer_x": 250,
            "pointer_y": 180
        }
    ],
    "request_id": "req_abc123"
}
```

#### 响应

```json
{
    "code": 200,
    "message": "ok",
    "data": {
        "student_id": "stu_12345",
        "session_id": "session_67890",
        "assessment_type": "schelter_grid",
        "dimensions": [
            {
                "dimension": "注意力",
                "score": 72.5,
                "percentile": 68,
                "level": "良好",
                "raw_metrics": {
                    "avg_reaction_time_ms": 520,
                    "accuracy": 0.85,
                    "consistency": 0.78
                }
            },
            {
                "dimension": "工作记忆",
                "score": 58.2,
                "percentile": 35,
                "level": "中等",
                "raw_metrics": {}
            },
            {
                "dimension": "逻辑推理",
                "score": 85.7,
                "percentile": 92,
                "level": "优秀",
                "raw_metrics": {}
            }
        ],
        "overall_score": 72.1,
        "needs_attention": ["工作记忆"],
        "quick_suggestions": [
            "建议加强工作记忆训练",
            "逻辑推理能力表现出色"
        ],
        "generated_at": "2026-05-19T10:30:00Z"
    }
}
```

### 6.3 报告生成 API

#### 请求

```json
// POST /api/v1/reports/generate
{
    "student_id": "stu_12345",
    "assessment_result_ids": [1, 2, 3],
    "cognitive_profile": {
        "dimensions": [...],
        "overall_score": 72.1
    },
    "history": {
        "previous_scores": {
            "2026-03-15": 68.5,
            "2026-04-20": 70.2
        }
    },
    "include_trend_analysis": true,
    "request_id": "req_def456"
}
```

#### 响应

```json
{
    "code": 200,
    "data": {
        "student_id": "stu_12345",
        "report_id": "rpt_789012",
        "report": "### 综合评估...[详细报告内容]",
        "version": "1.0",
        "generated_at": "2026-05-19T10:30:00Z",
        "llm_model": "qwen-turbo",
        "token_usage": {
            "prompt_tokens": 2500,
            "completion_tokens": 1800,
            "total_tokens": 4300
        },
        "has_ai_disclaimer": true,
        "is_safe": true
    }
}
```

### 6.4 训练推荐 API

#### 请求

```json
// POST /api/v1/training/plans
{
    "student_id": "stu_12345",
    "cognitive_profile": {
        "dimensions": [...]
    },
    "preferences": {
        "preferred_type": ["DIGITAL", "PHYSICAL"],
        "max_duration_min": 30,
        "exclude_exercises": ["exercise_123"]
    },
    "request_id": "req_ghi789"
}
```

#### 响应

```json
{
    "code": 200,
    "data": {
        "plan_id": "plan_stu_12345_1716105000",
        "student_id": "stu_12345",
        "objectives": [
            "将工作记忆能力从58提升至75",
            "保持逻辑推理能力的优秀水平"
        ],
        "exercises": [
            {
                "id": "exer_mem_001",
                "name": "数字广度训练",
                "type": "DIGITAL",
                "duration_min": 15,
                "difficulty": 2,
                "description": "通过数字序列回忆训练工作记忆...",
                "expected_benefit": "工作记忆容量增加"
            }
        ],
        "weekly_schedule": {
            "Monday": ["exer_mem_001"],
            "Tuesday": ["exer_mem_002"],
            ...
        },
        "duration_weeks": 4,
        "preview_week": 1,
        "generated_at": "2026-05-19T10:30:00Z"
    }
}
```

## 7. 技术架构细节

### 7.1 依赖关系

```python
# requirements.txt
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3

# LLM & NLP
langchain==0.1.9
langchain-openai==0.0.5
openai==1.10.0
tiktoken==0.6.0
sentence-transformers==2.3.1
transformers==4.37.0

# 向量数据库
pymilvus==2.4.0
numpy==1.26.3

# 工具
redis==5.0.1
httpx==0.26.0
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
```

### 7.2 配置管理

```python
# app/core/config.py
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
```

## 8. 部署配置

### 8.1 Dockerfile

```dockerfile
# apps/ai-service/Dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('paraphrase-MiniLM-L6-v2')"

FROM python:3.11-slim

WORKDIR /app

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 复制依赖
COPY --from=builder /usr/local/lib/python3.11/site-packages \
    /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]
```

### 8.2 环境变量示例

```bash
# .env
APP_NAME=BrainSpark AI Service
VERSION=0.1.0
DEBUG=false

MILVUS_URI=http://milvus:19530
MILVUS_COLLECTION=brainspark_knowledge

REDIS_URL=redis://redis:6379/0

OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_API_KEY=${DASHSCOPE_API_KEY}
DEFAULT_MODEL=qwen-turbo

MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

RATE_LIMIT_REQUESTS=200
RATE_LIMIT_WINDOW=60
```

### 8.3 Docker Compose

```yaml
version: '3.8'
services:
  ai-service:
    build: ./apps/ai-service
    ports:
      - "8001:8001"
    environment:
      - MILVUS_URI=http://milvus:19530
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - milvus
      - redis
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
```

## 9. 性能指标

| 指标 | 目标值 |
|------|--------|
| API P95 响应时间 (分析) | < 500ms |
| API P95 响应时间 (报告生成) | < 5s |
| API P95 响应时间 (知识搜索) | < 200ms |
| 向量检索准确率 | > 85% |
| 报告安全通过率 | > 99% |
| 并发请求支持 | > 100 QPS |