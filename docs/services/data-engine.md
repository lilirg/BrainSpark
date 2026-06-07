# BrainSpark AI 与数据引擎层详细设计文档

> **实现状态: 规划中** — 当前项目中尚无 `apps/data-engine` 目录或相关代码。本文档描述的是目标架构设计，待后续迭代实现。

> 本文档详细描述 BrainSpark 平台的"AI 与数据引擎层"架构设计，包含行为数据清洗（Kafka + Flink）、特征工程与常模分析（ClickHouse）、RAG 评估引擎。

## 1. 数据引擎总览

```
┌─────────────────────────────────────────────────────────────────────┐
│                   AI & Data Engine Layer  【规划中】                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  数据流入                                                      │  │
│  │  Go Gateway ──Kafka──► Kafka Topics                           │  │
│  │         event.ingestion                                       │  │
│  │         assessment.complete                                   │  │
│  └──────────────────────────┬────────────────────────────────────┘  │
│                             ▼                                        │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Flink 实时处理引擎                                             │  │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────────┐            │  │
│  │  │ 数据清洗   │ │ 行为聚合  │ │ 异常检测       │            │  │
│  │  │ & 校验    │ │          │ │ & 反作弊      │            │  │
│  │  └─────┬─────┘  └─────┬─────┘  └──────┬────────┘            │  │
│  └────────┼──────────────┼───────────────┼─────────────────────┘  │
│           ▼              ▼               ▼                        │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  数据存储层                                                    │  │
│  │  MongoDB (原始事件)  ──► ClickHouse (分析/常模)               │  │
│  └─────────────────────────────┬─────────────────────────────────┘  │
│                                 ▼                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  AI 分析引擎                                                    │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐  │  │
│  │  │ 特征工程     │  │ 常模对比      │  │ RAG 报告生成          │  │  │
│  │  │             │  │              │  │                      │  │  │
│  │  │ 反应时分析   │  │ 年龄分组     │  │ 向量检索            │  │  │
│  │  │ 正确率统计   │  │ Z-Score     │  │ Prompt 工程          │  │  │
│  │  │ 轨迹质量    │  │ 百分位计算   │  │ LLM 生成             │  │  │
│  │  └──────┬──────┘  └──────┬───────┘  └──────────┬───────────┘  │  │
│  └─────────┼────────────────┼──────────────────────┼─────────────┘  │
│            ▼                ▼                      ▼                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  结果存储与输出                                                │  │
│  │  MySQL: 认知分数 / 常模百分位                                  │  │
│  │  Milvus: 教育知识向量                                          │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. 行为数据清洗 pipeline (Kafka + Flink)

### 2.1 架构概览

```
学生端采集 ──► Go Gateway ──Kafka─► Flink Source ──► Flink Transform ──► Flink Sink
                                                              ├── MongoDB
                                                              ├── ClickHouse
                                                              └── Redis (实时缓存)
```

### 2.2 Kafka 消息主题设计

```yaml
# Kafka Topics
- event.ingestion.raw: 3 partitions, retention 3 days, key = student_id
- event.ingestion.validated: 3 partitions, retention 7 days, key = student_id  
- event.processing.agg: 3 partitions, retention 30 days, key = session_id
- report.generation: 1 partition, key = user_id
- assessment.complete: 1 partition, key = session_id
- notification.push: 6 partitions (根据 user_id mod 6)
```

### 2.3 Flink 作业设计

```java
// FlinkJob.java - 实时数据处理主入口
public class FlinkJob {
    
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(3);
        env.enableCheckpointing(60_000); // 60s checkpoint
        env.getCheckpointConfig().setCheckpointTimeout(300_000);
        
        // Kafka Source
        KafkaSource<String> kafkaSource = KafkaSource.<String>builder()
            .setBootstrapServers(KAFKA_BOOTSTRAP_SERVERS)
            .setTopics("event.ingestion.raw")
            .setGroupId("brainspark-flink")
            .setValueOnlyDeserializer(new StringSchemaDeserializer())
            .setStartingOffsets(OffsetsInitializer.committedOffsets(OffsetResetStrategy.LATEST))
            .build();
        
        DataStream<String> rawStream = env.fromSource(kafkaSource, WatermarkStrategy.noWatermarks(), "KafkaSource");
        
        // 1. 清洗 & 校验
        DataStream<EventRecord> validatedStream = rawStream
            .map(new JsonDeserializationFunction<>(EventRecord.class))
            .filter(new EventValidator())  // 过滤无效事件
            .flatMap(new EnrichmentMapper())  // 补充设备信息、会话 ID 等
            .name("EventCleaning");
        
        // 2. 写入 MongoDB (原始事件)
        validatedStream.addSink(new MongoSink(MONGO_URI))
            .name("WriteMongoDB");
        
        // 3. 行为聚合 (Session Window)
        DataStream<EventAgg> aggStream = validatedStream
            .keyBy(EventRecord::getSessionId)
            .window(EventTimeSessionWindows.withGap(Time.minutes(15)))
            .aggregate(new SessionAggregator())
            .name("SessionAggregation");
        
        // 4. 反作弊检测
        DataStream<CheatingFlag> cheaterStream = validatedStream
            .keyBy(EventRecord::getUserId)
            .process(new AntiCheatingProcessor())
            .name("AntiCheatingCheck");
        
        // 5. 聚合结果写入 Kafka
        aggStream.map(AggRecord::toJson)
            .addSink(KafkaSink.newBuilder().setBootstrapServers(KAFKA_BOOTSTRAP_SERVERS)
                .setWriter(new KafkaEventWriter("event.processing.agg"))
                .build())
            .name("WriteToKafka");
        
        env.execute("BrainSpark Realtime Data Pipeline");
    }
}

// 事件验证器
public class EventValidator implements FilterFunction<EventRecord> {
    @Override
    public boolean filter(EventRecord record) {
        // 基本校验
        if (record.getEventId() == null || record.getUserId() == null) {
            return false;
        }
        
        // 生理极限校验
        Long reactionTime = record.getReactionTimeMs();
        if (reactionTime != null) {
            // <150ms 为不可能 (人类生理极限)
            if (reactionTime < 150 || reactionTime > 30000) {
                return false; // 丢弃异常数据
            }
        }
        
        // 时间合法性
        if (record.getTimestamp() == null || record.getTimestamp() < 0) {
            return false;
        }
        
        return true;
    }
}

// 反作弊检测器
public class AntiCheatingProcessor extends KeyedProcessFunction<Long, EventRecord, CheatingFlag> {
    
    private final transient ValueState<CheatScore> cheatScoreState;
    
    public AntiCheatingProcessor() {
        cheatScoreState = getRuntimeContext()
            .getState(new ValueStateDescriptor<>("cheat_score", CheatScore.class));
    }
    
    @Override
    public void processElement(EventRecord record, Context ctx, Collector<CheatingFlag> out) 
            throws Exception {
        
        CheatScore score = cheatScoreState.value();
        if (score == null) {
            score = new CheatScore(record.getUserId(), 0L, new ArrayList<>());
        }
        
        // 检测异常模式
        if (record.getReactionTimeMs() != null) {
            long rt = record.getReactionTimeMs();
            if (rt < 200) {
                // <200ms 记 1 分
                score.setScore(score.getScore() + 1);
            }
        }
        
        // 记录最近异常事件 (滑动窗口)
        long now = ctx.timestamp();
        score.getRecentViolations().add(now);
        score.getRecentViolations().removeIf(t -> now - t > 300_000); // 5 分钟窗口
        
        cheatScoreState.update(score);
        
        // 超过阈值则标记
        if (score.getScore() > 10 || score.getRecentViolations().size() > 20) {
            out.collect(new CheatingFlag(
                record.getUserId(),
                record.getSessionId(),
                "HIGH_FREQ_RAPID_CLICKS",
                score.getScore()
            ));
        }
    }
}
```

### 2.4 数据模型定义

```proto
// event.proto - Flink 消息体
message EventRecord {
    string event_id = 1;
    int64 user_id = 2;
    string session_id = 3;
    string task_id = 4;
    string event_type = 5;      // CLICK, HOVER, PRESS, RELEASE, NAVIGATE
    float performance_now = 6;   // performance.now() 精确值 (毫秒)
    int64 reaction_time_ms = 7;
    float pointer_x = 8;
    float pointer_y = 9;
    float pointer_pressure = 10;
    DeviceInfo device_info = 11;
    int64 created_at = 12;       // Unix millis
    map<string, string> metadata = 13;
}

message DeviceInfo {
    int32 screen_width = 1;
    int32 screen_height = 2;
    float pixel_ratio = 3;
    string browser = 4;
    string os = 5;
    string device_model = 6;
}

message CheatingFlag {
    int64 user_id = 1;
    string session_id = 2;
    string flag_type = 3;        // REACTION_TOO_FAST, ANOMALOUS_TRAJECTORY
    int32 severity_score = 4;    // 严重程度 1-10
    string details = 5;
    int64 detected_at = 6;
}
```

```sql
-- MongoDB 集合: event_records
-- 结构见 business-backend-design.md 3.3 MongoDB 集合设计

-- MongoDB TTL 索引
db.event_records.createIndex(
    { "created_at": 1 },
    { expireAfterSeconds: 2592000 }  -- 30 天过期
)
```

## 3. 特征工程与常模分析 (ClickHouse)

### 3.1 ClickHouse 表结构设计

```sql
-- 用户原始测评事件表
CREATE TABLE assessment_event_records (
    event_id String,
    user_id Int64,
    session_id String,
    task_id String,
    type_code LowCardinality(String),       -- 测评类型编码
    event_type LowCardinality(String),      -- CLICK, HOVER, NAVIGATE
    grid_cell UInt8,                         -- 点击的格子编号 (1-25 for 5x5)
    performance_now Decimal64(6),            -- microsecond accuracy
    reaction_time_ms UInt16,                 -- 反应时 (0-65535 ms)
    pointer_x Float32,
    pointer_y Float32,
    correct UInt8,                          -- 正确 0/1
    created_at DateTime,
    request_id String,
    INDEX idx_user_time (user_id, created_at) TYPE minmax GRANULARITY 4
) ENGINE = MergeTree()
ORDER BY (user_id, created_at)
SETTINGS index_granularity = 8192;

-- 用户测评结果聚合表
CREATE TABLE assessment_results_agg (
    result_id String,
    user_id Int64,
    session_id String,
    task_id String,
    type_code LowCardinality(String),
    -- 基础统计
    total_clicks UInt32,
    correct_clicks UInt32,
    -- 反应时统计
    avg_reaction_time_ms UInt16,
    min_reaction_time_ms UInt16,
    p50_reaction_time_ms UInt16,
    p95_reaction_time_ms UInt16,
    sd_reaction_time_ms Float32,
    -- 路径分析
    total_path_length Float32,
    avg_path_angle Float32,
    -- 结果
    grid_size UInt8,
    total_time_sec Float32,
    score_value Float32,                   -- 原始分数
    -- 反作弊
    is_flagged UInt8 DEFAULT 0,
    flag_type LowCardinality(String) DEFAULT '',
    validity_status LowCardinality(String), -- VALID, FLAGGED, INVALID
    -- 时间
    started_at DateTime,
    completed_at DateTime,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (user_id, started_at)
SETTINGS index_granularity = 8192;

-- 教育常模表 (存储各年龄组各维度的统计分布)
CREATE TABLE cognitive_normalize (
    id UInt64,
    age_group LowCardinality(String),    -- "6-8", "9-11", "12-14", "15-17"
    dimension LowCardinality(String),     -- VISUAL_ATTENTION, WORKING_MEMORY, LOGIC
    score_mean Float32,                   -- 均值
    score_std Float32,                    -- 标准差
    p25 Float32,                          -- 25th percentile
    p50 Float32,                          -- 50th percentile (median)
    p75 Float32,                          -- 75th percentile
    p95 Float32,                          -- 95th percentile
    n UInt32,                             -- 样本量
    updated_at DateTime DEFAULT now(),
    INDEX idx_age_dim (age_group, dimension) TYPE bm25 GRANULARITY 1
) ENGINE = MergeTree()
ORDER BY (dimension, age_group)
SETTINGS index_granularity = 8192;

-- 教育知识库表 (Milvus 外也保存一份用于快速检索标题/标签)
CREATE TABLE education_knowledge (
    id UInt64,
    category LowCardinality(String),       -- 类别 (注意力训练, 记忆提升, 逻辑推理)
    title String,
    content String,
    source String,                         -- 来源 (学术文献/教育专家)
    tags Array(String),                    -- 标签
    embedding_version Int32,               -- 对应向量版本
    version Int32,
    created_at DateTime,
    updated_at DateTime DEFAULT now(),
    INDEX idx_category (category) TYPE tokenbf_v255 GRANULARITY 1,
    INDEX idx_tags (tags) TYPE bloom_filter GRANULARITY 1
) ENGINE = MergeTree()
ORDER BY (category, created_at)
```

### 3.2 常模对比计算

```sql
-- 计算百分位数的查询
SELECT 
    ar.result_id,
    ar.user_id,
    ar.dimension,
    ar.score_value,
    n.age_group,
    round(
        (sum(ar.score_value > n.p25) + sum(ar.score_value > n.p50) + 
         sum(ar.score_value > n.p75)) / n.n * 100
    , 1) as percentile,
    CASE 
        WHEN ar.score_value >= n.p95 THEN 'Excellent'
        WHEN ar.score_value >= n.p75 THEN 'Good'
        WHEN ar.score_value >= n.p25 THEN 'Average'
        ELSE 'Needs Improvement'
    END as level
FROM assessment_results_agg ar
LEFT JOIN cognitive_normalize n ON ar.dimension = n.dimension 
    AND ar.age_group = n.age_group
WHERE ar.result_id = 'some_result_id'
```

### 3.3 ClickHouse 查询优化

```sql
-- 获取用户历次认知能力数据 (按日期分组)
SELECT 
    toDate(started_at) as report_date,
    round(avg(score_value), 1) as avg_score,
    argMax(session_id, created_at) as last_session,
    count() as attempts
FROM assessment_results_agg
WHERE user_id = 12345
  AND started_at >= now() - INTERVAL 6 MONTH
GROUP BY report_date
ORDER BY report_date
```

```sql
-- 按年龄组统计某测试的平均数据 (用于常模校准)
SELECT 
    age_group,
    dimension,
    count() as sample_count,
    avg(score_value) as mean,
    stddevPop(score_value) as std,
    quantile(0.5)(score_value) as median,
    quantile(0.95)(score_value) as p95
FROM assessment_results_agg
WHERE started_at >= now() - INTERVAL 1 YEAR
GROUP BY age_group, dimension
HAVING sample_count >= 100
```

### 3.4 常模管理流程

```
1. 管理员 / 教育专家上传常模 CSV/Excel 
   │
2. Python 脚本校验常模数据合法性 (样本量/年龄区间/统计一致性)
   │
3. 写入 cognitive_normalize 表
   │
4. 对比新版本 (如果变更)
   │
5. 激活生效 (或排期下周一零点切换)
```

```sql
-- 常模数据版本管理
CREATE TABLE normalize_version (
    id UInt64,
    version String,
    effective_date Date,
    created_at DateTime,
    created_by String,
    change_log String -- JSON 变更日志
) ENGINE = MergeTree()
ORDER BY id;

-- 当前激活版本设置
SELECT version FROM normalize_version 
WHERE active = 1 LIMIT 1;
```

## 4. RAG 评估引擎设计

### 4.1 RAG 流程图

```
用户请求评估报告
  │
  ▼
1. 获取测评数据 (MySQL: assessment_results_agg)
  │
  ▼
2. 行为分析 & 特征提取 (ClickHouse: 反应时/正确率/轨迹分析)
  │
  ▼
3. 生成评估查询词 (如 "记忆力偏低但注意力正常的9岁儿童建议")
  │
  ▼
4. 向量检索 (Milvus: 检索相关教育干预策略、学习场景策略)
  │
  ├─ 步骤 4a: Embedding 查询向量
  ├─ 步骤 4b: 向量相似检索 (IP 余弦 / L2)
  ├─ 步骤 4c: Cross-Encoder Re-Rank (Top-3)
  └─ 步骤 4d: 拼接知识摘要
  │
  ▼
5. LLM 生成报告 (Qwen-Plus / ChatGPT-4o-mini 等)
  │
  ▼
6. 安全过滤 (关键词/正则 + LLM self-check)
  │
  ▼
7. 返回最终报告
```

### 4.2 教育知识库设计

```sql
-- 知识管理表 (MySQL)
CREATE TABLE knowledge_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    doc_id VARCHAR(64) NOT NULL UNIQUE,        -- 映射到 Milvus ID
    doc_title VARCHAR(200) NOT NULL,
    doc_content_short TEXT,                    -- 简短摘要
    doc_content_full LONGTEXT,                 -- 完整文本 (用于预览)
    category VARCHAR(50),                      -- CATEGORY, TYPE
    tags ARRAY(String),                        -- 标签
    embedding_dim Int32 DEFAULT 1536,
    embedding_version Int32 DEFAULT 1,
    source VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 4.3 知识向量化流程

```python
# app/services/embedding_service.py
class EmbeddingService:
    """统一 Embedding 服务"""
    
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL  # text-embedding-ada-002 or bge-large
        self.embedding_model = None
        self.dimensions = {
            'ada-002': 1536,
            'bge-large': 1024,
        }
    
    def embed_single(self, text: str) -> List[float]:
        if text is None:
            return []
        text = text[:2048]  # 截断
        embedding = self.model.encode(text)
        return (embedding / np.linalg.norm(embedding)).tolist()
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts)
```

### 4.4 RAG Prompt 设计

```python
# app/prompts/report_prompt.py
ANALYSIS_SYSTEM_PROMPT = """你是一位资深的儿童认知心理学专家及教育咨询师。请根据以下评估数据，生成一份科学、温暖、可执行能力的报告。

重要规则：
1. 严禁输出诊断性医疗术语（如 ADHD、自闭症、智力障碍、学习困难症）。
2. 不要使用伪科学术语（如"天赋测试"、"最强大脑"、"智商"）。
3. 所有建议基于实证教育科学研究（Cite 参考文献 ID 如 [1]、[2]）；若知识库无匹配则不要编造。
4. 语气温暖、专业、积极向上。
5. 使用"可以""建议""推荐"等建议性语言，避免"应该""必须"等强制性语言。
6. 所有建议必须具体、可操作：不只是"加强注意力训练"，而是"建议孩子每天玩5分钟舒尔特方格白卡游戏"。
7. 报告以"我们"而不是"你"开头，增强共情感。
8. 最后附上声明："本报告由 BrainSpark AI 辅助生成，仅供教育参考，不构成专业医疗诊断。"
"""
```

```python
# app/services/report_generator.py
from app.services.embedding_service import EmbeddingService
from app.rag.vector_store import MilvusVectorStore
from app.prompts.assessment_prompt import ANALYSIS_SYSTEM_PROMPT
from langchain_openai import ChatOpenAI

class ReportGenerator:
    """RAG 报告生成引擎"""
    
    def __init__(self, llm: ChatOpenAI, vector_store: MilvusVectorStore):
        self.llm = llm
        self.vector_store = vector_store
    
    async def generate(self, result_id: str) -> str:
        # Step 1: 从 ClickHouse 查询测评特征 + 常模百分位
        profile = self._fetch_assessment_profile(result_id)
        
        # Step 2: 构建 RAG 查询
        query_text = self._build_rag_query(profile)
        
        # Step 3: Milvus 检索相关教育知识 (Top-K)
        docs = await self.vector_store.similarity_search(query_text, k=5)
        
        # Step 4: 生成 LLM Prompt
        user_prompt = f"""
## 评估对象
- 年龄: {profile['age']} 岁
- 测评类型: {profile['type_code']}
- 测评日期: {profile['started_at']}

## 评估结果摘要
```json
{json.dumps(profile.get('dimensions'), ensure_ascii=False, indent=2)}
```

## 参考知识库 ({len(docs)} 条)
"""
        for i, doc in enumerate(docs):
            user_prompt += f"\n[{i+1}] {doc['title']}\n{doc['content_short']}\n"
        
        user_prompt += "\n## 报告"
        
        # Step 5: 调用 LLM
        messages = [
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.llm.ainvoke(messages)
        
        # Step 6: 安全审查
        final_report = await self.safety_filter(response.content)
        
        # Step 7: 持久化存储
        report_id = self._save_report(result_id, final_report, doc_ids=[d['id'] for d in docs])
        
        return final_report
    
    def _build_rag_query(self, profile: dict) -> str:
        """
        生成最佳的知识检索查询词：
        - 取最低的两个维度作为重点查询方向
        - 加入年龄信息 (策略随年龄差异很大)
        """
        dims = sorted(
            profile['dimensions'].items(),
            key=lambda x: x[1]['percentile'],
            reverse=False
        )
        low_dims = [d[0] for d in dims[:2]]
        age = profile.get('age', 10)
        
        queries = [f"低{d}的{age}岁儿童训练", d for d in low_dims]
        return ", ".join(queries)
    
    async def safety_filter(self, content: str) -> str:
        """安全过滤：确保内容合规"""
        blocked_words = [
            "天赋", "天才", "最强大脑", "智商低",
            "自闭症", "多动症", "ADHD", "学习能力差"
        ]
        
        # Replace 替换
        cleaned = content
        for word in blocked_words:
            cleaned = cleaned.replace(word, "[内容已优化]")
        
        # Prepend disclaimer
        disclaimer = "\n\n---\n⚠️ 本报告由 AI 辅助生成，仅供参考，不构成医学或专业诊断结论。如需更专业评估，请咨询医生或心理咨询师。\n"
        return cleaned + disclaimer
```

### 4.5 Milvus Collection Schema (完整实现)

```python
# app/rag/vector_store.py
from pymilvus import (
    connections, Collection, CollectionSchema, FieldSchema, DataType, utility
)
from langchain.schema import Document
from app.core.config import settings

MILVUS_HOST = settings.MILVUS_HOST  # "milvus"
MILVUS_PORT = settings.MILVUS_PORT  # 19530
CONNECTION_ALIAS = "default"
COLLECTION_NAME = settings.MILVUS_COLLECTION  # "brainspark_knowledge"
VECTOR_DIM = 1536  # OpenAI ada-002 / text-embedding-v3

class MilvusVectorStore:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init = False
        return cls._instance
    
    def __init__(self):
        if self._init:
            return
        self._init = True
        
        self._connect()
        if not utility.has_collection(COLLECTION_NAME, using=CONNECTION_ALIAS):
            self._create_collection()
        self._load_collection()
        self._create_index()
    
    def _connect(self):
        if not connections.list_connections():
            connections.connect(alias=CONNECTION_ALIAS, host=MILVUS_HOST, port=MILVUS_PORT)
    
    def _create_collection(self):
        """
        创建一个 Milvus 集合存储教育知识库的 doc: 字段 id, doc_title, doc_content_full, doc_content_short, category, tags, embedding, version, created_at
        """
        schema = CollectionSchema([
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
            FieldSchema(name="doc_title", dtype=DataType.VARCHAR, max_length=200),
            FieldSchema(name="doc_content_short", dtype=DataType.VARCHAR, max_length=4096),
            FieldSchema(name="doc_content_full", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="tags", dtype=DataType.ARRAY, elem_type=DataType.VARCHAR, max_capacity=20),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM),
            FieldSchema(name="version", dtype=DataType.INT32),
            FieldSchema(name="created_at", dtype=DataType.INT64),
        ], description="教育知识库集合")
        
        self.collection = Collection(COLLECTION_NAME, schema, using=CONNECTION_ALIAS)
    
    def _create_index(self):
        """创建 HNSW 向量索引 + 标量索引"""
        index_params = {
            "index_type": "HNSW",
            "metric_type": "IP",
            "params": {"M": 16, "efConstruction": 256}
        }
        self.collection.create_index("embedding", index_params)
        self.collection.create_index("category", {"index_type": "INVERTED"})
    
    def _load_collection(self):
        self.collection.load()
    
    async def search(
        self, 
        query_embedding: list[float],
        limit: int = 5,
        filter_expr: str = None
    ) -> List[dict]:
        """相似性搜索"""
        search_params = {
            "metric_type": "IP",
            "params": {"ef": 128}
        }
        
        expr = filter_expr if filter_expr else None
        
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=limit,
            expr=expr,
            output_fields=["id", "doc_title", "doc_content_short", "doc_content_full", "category", "tags", "version"]
        )
        
        results = [hit.entity.to_dict() for hits in results for hit in hits]
        for r in results:
            r["similarity"] = float(r["distance"])
        return results
    
    async def search_by_text(
        self,
        query_text: str,
        embedding_model,
        limit: int = 5,
        category: str = None
    ) -> List[dict]:
        """通过文本检索 (先 encode 再搜索)"""
        # TODO: Call embedding model to encode
        query_emb = await self._embed_text(query_text, embedding_model)
        
        filter_expr = f'category == "{category}"' if category else None
        return await self.search(query_emb, limit, filter_expr)
    
    async def add_documents(
        self,
        docs: List[dict],
        embedding_model
    ) -> List[str]:
        """
        向向量库添加文档
        参数:
        - docs: List of dicts. Each doc needs: id, doc_title, doc_content_short, doc_content_full, category, tags
        """
        embeddings = []
        ids = []
        
        for doc in docs:
            emb = await self._embed_text(doc["doc_content_full"], embedding_model)
            embeddings.append(emb)
            ids.append(doc["id"])
        
        entities = [
            ids,
            [d["doc_title"] for d in docs],
            [d["doc_content_short"] for d in docs],
            [d["doc_content_full"] for d in docs],
            [d["category"] for d in docs],
            [[str(t) for t in d.get("tags", [])] for d in docs],
            embeddings,
            [d.get("version", 1) for d in docs],
            [int(time.time()) for _ in ids]
        ]
        
        self.collection.insert(entities)
        self.collection.flush()
        return ids
    
    @asynccontextmanager
    async def close(self):
        self.collection.release()
        connections.disconnect(CONNECTION_ALIAS)
    
    async def _embed_text(self, text: str, model) -> list[float]:
        """Embedding"""
        return (await model.aembed_query(text[:4096]))
```

## 5. 数据处理 pipeline (完整流程图)

```mermaid
flowchart LR
    subgraph Source【规划中】
        A[Student Web] -->|事件数据 HTTP 上报| B(Go Gateway)
    end
    
    subgraph EventIngestion
        B -->|Kafka| C[event.ingestion.raw]
        B -->|批量写入| D[(MySQL: assessment_events)]
    end
    
    subgraph FlinkProcessing
        C --> E[Flink Job: 清洗/验证]
        E -->|过滤 & 标准化| F[event.ingestion.validated]
        E -->|反作弊标记| G[CheatFlag Table]
    end
    
    subgraph Storage
        F --> H[(MongoDB: event_records)]
        F --> I[ClickHouse: assessment_event_records]
    end
    
    subgraph Processing
        I --> J[Batch Job: 每日聚合 → assessment_results_agg]
        J --> K[ClickHouse: 计算百分位, 标记异常]
        K --> L[(MySQL: reports / assessment_profiles)]
    end
```

### 5.1 Kafka Topics 详细配置

| Topic | Partitions | Replication | Retention | Key |
|-------|-----------|-------------|-----------|-----|
| `event.ingestion.raw` | 6 | 3 | 3 天 | user_id |
| `event.ingestion.validated` | 6 | 3 | 7 天 | user_id |
| `event.processing.agg` | 3 | 3 | 30 天 | session_id |
| `report.generation` | 1 | 3 | 永久 | user_id |
| `assessment.complete` | 1 | 3 | 永久 | session_id |
| `notification.push` | 6 | 3 | 1 天 | user_id |
| `payment.completed` | 2 | 3 | 永久 | user_id |

---

## 6. 数据流图 (全链路)

```
用户交互 ──► PixiJS 事件捕获 (performance.now)
              │
              ▼
Go Gateway ──► Kafka event.ingestion.raw ──► Flink 清洗 / 反作弊检测
              │                                    │
              │              ┌─────────────────────┤
              │              ▼                     ▼
              │         event.ingestion.validated  Milvus / MongoDB
              │              │                     ClickHouse
              │              ▼
              │         event.processing.agg
              │              │
              ▼              ▼
MySQL (assessment_results) ──► Milvus → RAG Retrieval → LLM → Report Output
```

## 7. 配置管理

```yaml
# Flink 配置
flink:
  job:
    name: brainspark-data-pipeline
    parallelism: 3
    checkpoint-interval: 60000
    checkpoint-timeout: 300000
  kafka:
    bootstrap-servers: kafka:9092
    group-id: brainspark-flink
  mongodb:
    uri: mongodb://mongo:27017/brainspark_events
  clickhouse:
    jdbc: jdbc:clickhouse://clickhouse:8123/brainspark

# ClickHouse 查询参数
clickhouse:
  query:
    max-rows: 100000
    timeout-sec: 30
```

## 8. 性能指标

| 指标 | 目标 |
|------|------|
| Flink 端到端延迟 | < 3 秒 |
| Flink 吞吐量 | > 10,000 events/sec |
| ClickHouse 聚合查询 P95 | < 200ms |
| 常模百分位计算 P99 | < 500ms |
| Milvus 向量检索 P95 | < 100ms |
| RAG 报告生成 P95 | < 5s (含 LLM 推理) |

---

> **总结**: AI 与数据引擎层是整个 BrainSpark 平台的智能中枢，通过"高并发收集 → 实时 Flink 清洗 → ClickHouse 存储 + ClickHouse 特征 + Milvus RAG 检索 → LLM 生成"构建闭环。