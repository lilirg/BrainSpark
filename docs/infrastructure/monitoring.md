# BrainSpark 监控告警设计

> 本文档定义 BrainSpark 平台的监控体系，涵盖指标采集、告警规则、日志采集、链路追踪和告警通知五个方面，基于 Prometheus + Grafana + ELK/Loki + Jaeger 技术栈。

---

## 目录

- [指标采集](#指标采集)
  - [Prometheus 配置](#prometheus-配置)
  - [业务指标定义](#业务指标定义)
  - [JVM/Go Runtime 指标](#jvm Go-runtime-指标)
  - [中间件指标](#中间件指标)
- [告警规则](#告警规则)
  - [基础设施告警](#基础设施告警)
  - [应用层告警](#应用层告警)
  - [业务告警](#业务告警)
- [日志采集](#日志采集)
  - [ELK/Loki 配置](#ekllf-配置)
  - [日志级别规范](#日志级别规范)
  - [结构化日志格式](#结构化日志格式)
  - [日志保留策略](#日志保留策略)
- [链路追踪](#链路追踪)
  - [Jaeger/Zipkin 集成](#jaegerzipkin-集成)
  - [跨服务追踪](#跨服务追踪)
  - [关键链路埋点](#关键链路埋点)
- [告警通知](#告警通知)
  - [通知渠道](#通知渠道)
  - [告警分级](#告警分级)
  - [值班表管理](#值班表管理)

---

## 指标采集

### Prometheus 配置

#### 服务发现

采用 K8s Service Monitor 自动发现：

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # 抓取业务服务 (Java/Go/Python)
  - job_name: 'brainspark-apps'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names: ['brainspark']
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: '(backend-business|backend-gateway|ai-service)'
      - source_labels: [__meta_kubernetes_pod_label_monitoring]
        action: keep
        regex: 'enabled'

  # 抓取前端 (cAdvisor)
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  # 抓取 Node Exporter
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # 抓取中间件 Exporter
  - job_name: 'mysql-exporter'
    static_configs:
      - targets: ['mysql-exporter:9104']

  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'kafka-exporter'
    static_configs:
      - targets: ['kafka-exporter:9308']

# Alertmanager 配置
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
```

#### K8s ServiceMonitor 配置

```yaml
# infrastructure/k8s/monitoring/servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: brainspark-services
  namespace: brainspark
spec:
  selector:
    matchLabels:
      monitoring: enabled
  namespaces:
    - brainspark
  endpoints:
    - port: metrics
      interval: 15s
      path: /actuator/prometheus  # Java Spring Boot
      # 或 /metrics                  # Go Gin
```

### 业务指标定义

#### 核心指标 (Metrics)

```yaml
# 请求量 (QPS)
http_requests_total{method="GET|POST", status="200|500|404", handler="/api/v1/..." }

# 请求延迟 ( histogram/summary )
http_request_duration_seconds_bucket{le="0.1|0.5|1|5"}
http_request_duration_seconds_sum
http_request_duration_seconds_count

# 错误率 ( rate )
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# 活跃连接数
go_goroutines                          # Go 运行时
jvm_threads_live                       # JVM 运行时
redis_connected_clients                # Redis 客户端
kafka_consumer_group_lag               # Kafka 消费延迟

# 业务指标
brainspark_assessments_completed_total
brainspark_reports_generated_total
brainspark_orders_created_total
brainspark_user_login_total
```

#### 业务指标命名规范

| 模块 | Metric 前缀 |
|------|-------------|
| 用户服务 | `brainspark_user_` |
| 测评服务 | `brainspark_assessment_` |
| 报告服务 | `brainspark_report_` |
| 订单服务 | `brainspark_order_` |
| AI 服务 | `brainspark_ai_` |
| 网关 | `brainspark_gateway_` |

### JVM/Go Runtime 指标

#### Java (Spring Boot 3 + Micrometer)

```yaml
# JVM 指标
jvm_memory_bytes_used{area="heap|nonheap"}
jvm_gc_pause_seconds_sum
jvm_threads_live_count
jvm_threads_peak_count

# Spring Boot
http_server_requests_seconds_bucket
tomcat_sessions_active_current_count
dataSource_usage_active
dataSource_usage_idle
```

#### Go (net/http + expvar + process_exporter)

```yaml
# Go 运行时
go_goroutines
go_memstats_alloc_bytes
go_gc_duration_seconds
go_info_version

# HTTP
http_request_duration_seconds_bucket
http_requests_total

# 进程
process_cpu_seconds_total
process_resident_memory_bytes
```

#### Python (FastAPI + prometheus-fastapi-instrumentor)

```yaml
# FastAPI
fastapi_request_duration_seconds_bucket
fastapi_requests_total

# 进程
process_cpu_seconds_total
process_resident_memory_bytes
```

### 中间件指标

#### MySQL

```yaml
mysql_global_status_threads_connected
mysql_global_status_queries
mysql_engine_innodb_data_reads
mysql_replication_seconds_behind_master
```

#### Redis

```yaml
redis_connected_clients
redis_memory_used_bytes
redis_commands_processed_total
redis_keyspace_hits_total
redis_keyspace_misses_total
```

#### Kafka

```yaml
kafka_consumer_group_lag
kafka_broker_topic_messages_in
kafka_consumer_fetch_rate_total
kafka_topic_partition_under_replicated
```

---

## 告警规则

### 基础设施告警

```yaml
# prometheus/alerting.yaml
groups:
  - name: infrastructure
    rules:
      # CPU 告警
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CPU 使用率过高 (>80%)"
          description: "{{ $labels.instance }} CPU 使用率 {{ $value }}%"

      # 内存告警
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "内存使用率过高 (>85%)"

      # Pod 重启告警
      - alert: PodCrashLooping
        expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pod {{ $labels.pod }} 频繁重启"

      # 磁盘告警
      - alert: HighDiskUsage
        expr: (node_filesystem_size_bytes - node_filesystem_available_bytes) / node_filesystem_size_bytes * 100 > 90
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "磁盘使用率过高 (>90%)"

      # 节点失联
      - alert: NodeDown
        expr: up{job="node-exporter"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "节点 {{ $labels.instance }} 失联"
```

### 应用层告警

```yaml
  - name: application
    rules:
      # 错误率告警 (>1%)
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) 
          / 
          sum(rate(http_requests_total[5m])) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "错误率过高 (>1%)"
          description: "{{ $labels.job }} 错误率 {{ $value | humanizePercentage }}"

      # P95 响应时间告警 (>1s)
      - alert: HighLatencyP95
        expr: |
          histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job)) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P95 响应时间过高 (>1s)"
          description: "{{ $labels.job }} P95 延迟 {{ $value }}s"

      # P99 响应时间告警 (>3s)
      - alert: HighLatencyP99
        expr: |
          histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job)) > 3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P99 响应时间过高 (>3s)"

      # 网关异常率
      - alert: GatewayHigh4xxRate
        expr: |
          sum(rate(backend_gateway_requests_total{status=~"4.."}[5m])) 
          / 
          sum(rate(backend_gateway_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "网关 4xx 错误率过高 (>5%)"

      # AI 服务超时
      - alert: AIServiceTimeout
        expr: sum(rate(ai_service_requests_total{status="408"}[5m])) > 10
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "AI 服务大量超时"
```

### 业务告警

```yaml
  - name: business
    rules:
      # 测评失败告警
      - alert: AssessmentFailure
        expr: sum(rate(brainspark_assessment_failed_total[5m])) > 5
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "测评失败数过多 (>5/分钟)"

      # 报告生成失败
      - alert: ReportGenerationFailure
        expr: sum(rate(brainspark_report_failed_total[5m])) > 3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "报告生成失败 (>3/分钟)"

      # 订单失败告警
      - alert: OrderCreationFailure
        expr: sum(rate(brainspark_order_failed_total[5m])) > 2
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "订单创建失败 (>2/分钟)"

      # 评估超时告警 (单次 > 30s)
      - alert: AssessmentTimeout
        expr: sum(brainspark_assessment_duration_seconds_bucket{le="+Inf"}) > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "评估耗时超长 (>30s) 请求数过多"

      # 家长端登录失败率
      - alert: ParentLoginFailure
        expr: sum(rate(backend_user_login_failed_total[5m])) > 20
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "家长端登录失败频繁 (>20/分钟)"

      # 订单金额异常
      - alert: AbnormalOrderAmount
        expr: sum(increase(brainspark_order_amount_bucket[1h])) > 50000
        for: 1h
        labels:
          severity: critical
        annotations:
          summary: "小时订单金额异常 (>¥50000)"
```

---

## 日志采集

### ELK/Loki 配置

#### 方案选择

| 方案 | 适用场景 |
|------|----------|
| ELK (Elasticsearch + Logstash + Kibana) | 需要全文检索、复杂分析 |
| Loki + Promtail + Grafana | 与 Prometheus 生态集成、成本更低 |

本项目推荐 **Loki** 为主，ELK 为辅（用于业务报表分析）：

#### Loki 配置

```yaml
# infrastructure/monitoring/loki/loki-config.yaml
auth_enabled: false

server:
  http_listen_port: 3100

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2020-01-01
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

limits_config:
  reject_old_samples: true
  reject_old_samples_max_age: 168h  # 7天
```

#### Logback 配置 (Java Spring Boot)

```xml
<!-- 输出 JSON 格式日志到 stdout，由 Promtail 采集 -->
<configuration>
    <appender name="LOKI" class="com.github.loki4j.logback.Loki4jAppender">
        <url>http://loki:3100/loki/api/v1/push</url>
        <format>
            <label>app=backend-business,host=${HOSTNAME},level=%level</label>
            <message>{"userId":"%X{userId:-}","traceId":"%X{traceId:-}","msg":"%msg"}</message>
        </format>
    </appender>

    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="ch.qos.logback.classic.encoder.JsonEncoder"/>
    </appender>

    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="LOKI"/>
    </root>
</configuration>
```

#### Go Structured Logger (Zap)

```go
// internal/handler/handler.go
import "go.uber.org/zap"

var logger *zap.SugaredLogger

func InitLogger() {
    config := zap.NewProductionConfig()
    config.EncoderConfig.TimeKey = "timestamp"
    config.EncoderConfig.EncodeTime = zap.ISO8601TimeEncoder
    logger, _ = config.Build()
}
```

#### Python logging 配置

```python
# app/core/logger.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if hasattr(record, 'trace_id'):
            log_data['trace_id'] = record.trace_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        return json.dumps(log_data, ensure_ascii=False)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
```

### 日志级别规范

| 级别 | 说明 | 使用场景 |
|------|------|----------|
| ERROR | 错误 | 异常、不可恢复错误、业务失败 |
| WARN | 警告 | 潜在风险、降级、重试 |
| INFO | 信息 | 重要业务事件、用户操作 |
| DEBUG | 调试 | 开发/调试细节，生产环境关闭 |
| TRACE | 跟踪 | 超详细追踪，仅问题排查时开启 |

### 结构化日志格式

#### 核心字段

```json
{
  "timestamp": "2026-05-19T09:00:00Z",
  "level": "INFO",
  "service": "backend-business",
  "instance": "backend-business-abc123",
  "trace_id": "a1b2c3d4e5f6",
  "span_id": "x9y8z7",
  "user_id": "user_12345",
  "module": "assessment",
  "action": "create_assessment",
  "message": "测评任务创建成功",
  "duration_ms": 150,
  "status": "success"
}
```

### 日志保留策略

| 环境 | 保留时间 | 存储策略 |
|------|----------|----------|
| 开发 | 7天 | Loki + 本地文件 |
| 预发 | 30天 | Loki |
| 生产 | 90天 | Loki + 冷数据转储至 S3 / OSS |

---

## 链路追踪

### Jaeger/Zipkin 集成

#### 技术选型

推荐使用 **Jaeger**（CNCF 项目，与 K8s 集成更紧密）：

```yaml
# infrastructure/monitoring/jaeger/jaeger-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
        - name: jaeger-collector
          image: jaegertracing/jaeger-collector:latest
          ports:
            - containerPort: 14268  # HTTP ingest
            - containerPort: 14250  # gRPC ingest
        - name: jaeger-query
          image: jaegertracing/jaeger-query:latest
          ports:
            - containerPort: 16686  # UI
          env:
            - name: COLLECTOR_ZIPKIN_HTTP_PORT
              value: "9411"
```

#### Java 集成 (Spring Boot)

```yaml
# application.yml
spring:
  sleuth:
    sampler:
      probability: 0.1  # 采样率 10%
  zipkin:
    base-url: http://jaeger:9411
    enabled: true

management:
  tracing:
    sampling:
      probability: 0.1
```

#### Go 集成 (otel + jaeger)

```go
// internal/middleware/tracing.go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/jaeger"
    "go.opentelemetry.io/otel/sdk/resource"
    semconv "go.opentelemetry.io/otel/semconv/v1.21.0"
)

func InitTracer(serviceName string) (func(), error) {
    endpoint := fmt.Sprintf("http://%s:%s", os.Getenv("JAEGER_HOST"), os.Getenv("JAEGER_PORT"))
    exporter, err := jaeger.New(jaeger.WithCollectorEndpoint(jaeger.WithEndpoint(endpoint)))
    if err != nil {
        return nil, err
    }

    tracerProvider := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceNameKey.String(serviceName),
        )),
    )

    otel.SetTracerProvider(tracerProvider)
    return tracerProvider.Shutdown, nil
}
```

#### Python 集成 (OpenTelemetry)

```python
# app/services/telemetry.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def setup_tracer(service_name: str):
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
```

### 跨服务追踪

#### Trace 传播机制

所有服务通过 HTTP Header (`Traceparent` / `X-B3-*`) 和消息队列 Header 传播 Trace ID：

```
┌────────────┐  API Request  ┌────────────┐  Message  ┌────────────┐
│  Frontend  │ ────────────► │  Gateway   │ ────────► │ Business   │
│  (Vue 3)   │               │  (Go Gin)  │           │  (Java)    │
└────────────┘               └─────┬──────┘           └─────┬──────┘
                                   │                         │
                          TraceID:                                TraceID:
                          parent_span:001                   parent_span:001
                                   │                         │
                                   │                    ┌────┴────┐
                                   │   AI Response      │   DB    │
                                   ────────────────────► │   AI Svc│
                                                         └────────┘
```

#### 关键 Header

| Header | 说明 |
|--------|------|
| `Traceparent` | W3C Trace Context 标准 |
| `X-B3-TraceId` | Zipkin Trace ID |
| `X-B3-SpanId` | 当前 Span ID |
| `X-B3-ParentSpanId` | 父 Span ID |

### 关键链路埋点

#### 测评流程埋点

```
用户提交测评
  ├─ [Trace] 网关校验 (4xx/5xx)
  ├─ [Span] 网关路由 → 业务服务 (HTTP)
  ├─ [Span] 业务服务验证用户权限 → MySQL
  ├─ [Span] 业务服务调用测评引擎
  │   ├─ [Span] 测评引擎加载测评配置 → Redis
  │   ├─ [Span] 实时分析答案 → 计算引擎
  │   └─ [Span] 缓存结果 → Redis
  ├─ [Trace] 异步发送结果事件到 Kafka
  ├─ [Span] AI 服务接收事件 → 生成报告 → LLM
  │   ├─ [Span] 加载 RAG 知识库 → Milvus
  │   └─ [Span] 调用 LLM 接口
  └─ [Span] 报告写入 MongoDB + MySQL
```

#### 埋点示例

```java
// Java 微服务 span 示例
@GetMapping("/api/v1/assessments")
public ResponseEntity<?> getAssessments(
        @RequestHeader(value = "X-B3-TraceId", required = false) String traceId) {
    
    Span span = tracer.nextSpan().name("backend:getAssessments").start();
    try (Tracer.SpanInScope ws = tracer.withContext(span.context())) {
        // 业务逻辑
        List<Assessment> assessments = assessmentService.getActiveAssessments(userId);
        span.tag("user.id", String.valueOf(userId));
        span.tag("assessments.count", String.valueOf(assessments.size()));
        return ResponseEntity.ok(assessments);
    } finally {
        span.finish();
    }
}
```

---

## 告警通知

### 通知渠道

#### Alertmanager 配置

```yaml
# infrastructure/monitoring/alertmanager/alertmanager.yml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'wechat-bot'
  routes:
    - match:
        severity: critical
      receiver: 'phone-oncall'
      repeat_interval: 1h
    - match:
        severity: warning
      receiver: 'wechat-bot'

receivers:
  - name: 'wechat-bot'
    webhook_configs:
      - url: 'http://wechat-bot:8080/alert'
        send_resolved: true

  - name: 'email-alert'
    email_configs:
      - to: 'devops@brainspark.com'
        from: 'alertmanager@brainspark.com'
        smarthost: 'smtp.brainspark.com:587'

  - name: 'phone-oncall'
    webhook_configs:
      - url: 'http://phone-escalation:8080/trigger'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'service']
```

### 告警分级

| 级别 | 级别标识 | 说明 | 响应时间 | 通知渠道 |
|------|----------|------|----------|----------|
| P0 | 灾难 | 系统宕机、数据丢失、支付失败 | 5分钟 | 电话 + 微信 + 短信 |
| P1 | 严重 | 核心功能不可用、错误率>5% | 15分钟 | 微信 + 短信 |
| P2 | 警告 | 非核心功能异常、错误率>1% | 1小时 | 微信机器人 |
| P3 | 提示 | 性能下降、容量预警 | 4小时 | 邮件 |

#### 告警升级机制

```
P0/P1 未处理 → 30 分钟 → 升级至技术总监
P2 未处理 → 2 小时 → 升级至技术负责人
P3 未处理 → 4 小时 → 升级至值班工程师
```

### 值班表管理

#### 值班表格式

```yaml
# infrastructure/monitoring/oncall-schedule.yaml
oncall_schedule:
  timezone: Asia/Shanghai
  rotation: weekly
  escalation_policy:
    - level: L1
      response_time: "15m"
      channels: [wechat]
    - level: L2
      response_time: "5m"
      channels: [wechat, phone]
    - level: L3
      response_time: "2m"
      channels: [phone, sms]

  roster:
    - week: 1
      engineers:
        - name: 张三
          email: zhangsan@brainspark.com
          phone: +86-138xxxx0001
          wechat_id: zhangsan_oncall
        - name: 李四
          email: lisi@brainspark.com
          phone: +86-138xxxx0002
    - week: 2
      engineers: ...
```

#### 集成企业微信/钉钉机器人

```python
# wechat_bot_notifier.py
import requests
import json

WECHAT_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"

def send_alert(title: str, content: str, level: str):
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"## {level} 告警\n"
                       f"**告警**: {title}\n"
                       f"**详情**: {content}\n"
                       f"**时间**: {__import__('datetime').datetime.utcnow().isoformat()}Z"
        }
    }
    requests.post(WECHAT_WEBHOOK, json=payload)
```

---

## 附录

### Dashboard 清单

| Dashboard | 来源 | 指标数 |
|-----------|------|--------|
| K8s Cluster Overview | Prometheus - node-exporter | ~50 |
| K8s Pod/Container | Prometheus - cAdvisor | ~30 |
| Java Application (Spring Boot) | Micrometer + Prometheus | ~100 |
| Go Application | Go metrics + Prometheus | ~30 |
| MySQL | MySQL Exporter | ~50 |
| Redis | Redis Exporter | ~40 |
| Kafka | Kafka Exporter | ~30 |
| 业务指标定制 Dashboard | 业务 Custom Exporter | ~60 |

### 参考文档

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Grafana Loki Documentation](https://grafana.com/docs/loki/latest/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)