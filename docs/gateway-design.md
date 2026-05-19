# BrainSpark 接入与网关层设计文档

> 本文档详细描述 BrainSpark 平台的接入层（Nginx 反向代理）与 API 网关层（Go 实现）的架构与设计。

## 1. 架构概述

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client Layer                                │
│   student-web  │   parent-web  │   teacher-web  │   operator-web     │
└───────────────┬──────────────────────────────┬──────────────────────┘
                │                              │
                ▼                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Access Layer (Nginx)                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  SSL Termination / HTTPS / HTTP2                              │  │
│  │                                                               │  │
│  │  Path-Based Routing:                                          │  │
│  │    /student/*    → student-web (port 3000)                    │  │
│  │    /parent/*     → parent-web (port 3001)                     │  │
│  │    /teacher/*    → teacher-web (port 3002)                    │  │
│  │    /operator/*   → operator-web (port 3003)                   │  │
│  │    /static/*     → 静态资源 (CDN 回源)                        │  │
│  │    /api/v1/*     → backend-gateway (port 8081)                │  │
│  │    /ai/v1/*      → ai-service (port 8000)                     │  │
│  │    /ws/*         → backend-gateway WebSocket (port 8082)      │  │
│  └───────────────────────────────────────────────────────────────┘  │
└───────────────┬──────────────────────────────┬──────────────────────┘
                │                              │
                ▼                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Gateway Layer                                    │
│  ┌─────────────────────┐    ┌───────────────────────────────────┐   │
│  │  Go API Gateway     │    │  Go WebSocket Gateway             │   │
│  │  (port 8081)         │    │  (port 8082)                      │   │
│  │                     │    │                                   │   │
│  │  ├─ Request ID      │    │  ├─ 实时游戏心跳/行为数据         │   │
│  │  ├─ Rate Limiter    │    │  ├─ 连接池管理                    │   │
│  │  ├─ JWT Auth (轻量) │    │  ├─ 帧同步/推送                   │   │
│  │  ├─ Request Validate│    │  └─ Disconnect 检测               │   │
│  │  └─ Response Format │    │                                   │   │
│  └─────────────────────┘    └───────────────────────────────────┘   │
└───────────────┬──────────────────────────────┬──────────────────────┘
                │                              │
                ▼                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Service Layer                                   │
│  ┌─────────────────────┐    ┌───────────────────────────────────┐   │
│  │  Java Backend       │    │  Python AI Service                │   │
│  │  (port 8080)         │    │  (port 8000)                      │   │
│  └─────────────────────┘    └───────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. Nginx 反向代理设计

### 2.1 配置文件

```nginx
# /etc/nginx/conf.d/brainspark.conf
upstream student_web {
    server 127.0.0.1:3000;
}

upstream parent_web {
    server 127.0.0.1:3001;
}

upstream teacher_web {
    server 127.0.0.1:3002;
}

upstream operator_web {
    server 127.0.0.1:3003;
}

upstream api_gateway {
    server 127.0.0.1:8081;
}

upstream ws_gateway {
    server 127.0.0.1:8082;
}

upstream ai_service {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl http2;
    server_namebrainspark.example.com;

    # SSL 配置
    ssl_certificate     /etc/nginx/ssl/brainspark.crt;
    ssl_certificate_key /etc/nginx/ssl/brainspark.key;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # 静态资源
    location /static/ {
        alias /var/www/brainspark/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Student Web
    location /student/ {
        proxy_pass http://student_web/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Parent Web
    location /parent/ {
        proxy_pass http://parent_web/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Teacher Web
    location /teacher/ {
        proxy_pass http://teacher_web/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Operator Web
    location /operator/ {
        proxy_pass http://operator_web/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API Gateway (HTTP)
    location /api/ {
        client_max_body_size 10M;
        proxy_pass http://api_gateway/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
    }

    # AI Service (HTTP)
    location /ai/ {
        client_max_body_size 50M;
        proxy_pass http://ai_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket Gateway
    location /ws/ {
        proxy_pass http://ws_gateway;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400s;  # 保持长连接
    }

    # 健康检查
    location /nginx-health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # 限流
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
    location /api/v1/events {
        limit_req zone=api_limit burst=200 nodelay;
        proxy_pass http://api_gateway;
    }
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name brainspark.example.com;
    return 301 https://$server_name$request_uri;
}
```

### 2.2 性能优化

```nginx
# /etc/nginx/nginx.conf
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 65535;
    use epoll;
    multi_accept on;
}

http {
    # 连接优化
    keepalive_timeout 75s;
    keepalive_requests 100;

    # 缓冲区优化
    client_body_buffer_size 16k;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 8k;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent"';

    access_log /var/log/nginx/access.log main buffer=32k flush=5s;
}
```

## 3. Go API 网关设计

### 3.1 目录结构

```
apps/backend-gateway/
├── cmd/
│   └── server/
│       └── main.go              # 入口（支持多端口启动）
├── internal/
│   ├── config/                  # 配置解析
│   │   └── config.go
│   ├── handler/                 # 路由处理
│   │   ├── assessment.go        # 游戏结果上报
│   │   ├── event.go             # 行为事件上报
│   │   ├── ws.go                # WebSocket handler
│   │   └── health.go            # 健康检查
│   ├── middleware/              # 中间件
│   │   ├── request_id.go        # Request ID 生成与传递
│   │   ├── rate_limiter.go      # 限流（Redis-backed）
│   │   ├── jwt_auth.go          # 轻量 JWT 校验
│   │   ├── request_validate.go  # 请求体校验
│   │   ├── cors.go              # CORS 处理
│   │   └── logging.go           # 结构化日志
│   ├── model/                   # 数据模型
│   │   ├── event.go             # 行为事件模型
│   │   ├── assessment.go        # 测评结果模型
│   │   └── response.go          # 统一响应格式
│   ├── writer/                  # 异步写入
│   │   ├── clickhouse.go        # ClickHouse 批量写入
│   │   ├── mongo.go             # MongoDB 写入
│   │   └── redis.go             # Redis 消息发布
│   ├── websocket/               # WebSocket 模块
│   │   ├── manager.go           # 连接池管理
│   │   ├── hub.go               # Hub pattern 广播
│   │   └── client.go            # 客户端会话
│   └── proxy/                   # 正向代理（透传业务 API）
│       └── router.go            # 路由到 Java/Python 服务
├── docker/
│   └── Dockerfile
├── go.mod
└── Makefile
```

### 3.2 多端口入口设计

[`cmd/server/main.go`](apps/backend-gateway/cmd/server/main.go)
```go
package main

import (
    "context"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/brainspark/gateway/internal/config"
    "github.com/brainspark/gateway/internal/handler"
    "github.com/brainspark/gateway/internal/middleware"
    "github.com/gin-gonic/gin"
)

func main() {
    cfg := config.Load()

    // HTTP 网关 (port 8081)
    httpSrv := startHTTPServer(cfg.HTTPPort)

    // WebSocket 网关 (port 8082)
    wsSrv := startWSServer(cfg.WSPort)

    // 优雅关闭
    gracefulShutdown(httpSrv, wsSrv)
}

func startHTTPServer(port string) *http.Server {
    r := gin.New()
    r.Use(gin.Recovery())
    r.Use(middleware.RequestID())
    r.Use(middleware.RateLimiter())
    r.Use(middleware.Logging())

    // API 路由
    api := r.Group("/api/v1")
    {
        api.POST("/assessment/results", handler.ReportAssessmentResults)
        api.POST("/events/behavior", handler.ReportBehaviorEvent)
        api.GET("/health", handler.HealthCheck)
    }

    // 透传路由（到 Java/Python 服务）
    router := middleware.NewReverseProxy()
    r.Use(router.Middleware())

    srv := &http.Server{
        Addr:              ":" + port,
        Handler:           r,
        ReadHeaderTimeout: 5 * time.Second,
        IdleTimeout:       120 * time.Second,
    }

    go func() {
        log.Printf("HTTP Gateway starting on :%s", port)
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatal(err)
        }
    }()
    return srv
}

func startWSServer(port string) *http.Server {
    hub := websocket.NewHub()
    go hub.Run()

    srv := &http.Server{
        Addr:    ":" + port,
        Handler: hub.HTTPHandler(),
    }

    go func() {
        log.Printf("WS Gateway starting on :%s", port)
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatal(err)
        }
    }()
    return srv
}
```

### 3.3 Request ID 中间件

```go
// internal/middleware/request_id.go
package middleware

import (
    "fmt"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/google/uuid"
)

const requestIDKey = "X-Request-ID"

func RequestID() gin.HandlerFunc {
    return func(c *gin.Context) {
        id := c.GetHeader(requestIDKey)
        if id == "" {
            id = generateRequestID()
        }
        c.Set(requestIDKey, id)
        c.Header(requestIDKey, id)
        c.Next()
    }
}

func generateRequestID() string {
    ts := time.Now().UnixMilli()
    u := uuid.New()
    return fmt.Sprintf("bs-%d-%s", ts, u.String()[:8])
}

// GetRequestID returns the current request ID from context
func GetRequestID(c *gin.Context) string {
    id, _ := c.Get(requestIDKey)
    s, _ := id.(string)
    return s
}
```

### 3.4 限流中间件（Redis 实现）

```go
// internal/middleware/rate_limiter.go
package middleware

import (
    "context"
    "time"

    "github.com/brainspark/gateway/internal/config"
    "github.com/redis/go-redis/v9"
    "github.com/gin-gonic/gin"
)

type RateLimiter struct {
    rdb   *redis.Client
    mode  string // "api" / "ws" / "event"
}

func NewRateLimiter(cfg config.RateLimiterConfig) *RateLimiter {
    rdb := redis.NewClient(&redis.Options{
        Addr:     cfg.RedisAddr,
        Password: cfg.RedisPassword,
        DB:       cfg.RedisDB,
    })
    return &RateLimiter{rdb: rdb, mode: cfg.Mode}
}

func (rl *RateLimiter) Limiter() gin.HandlerFunc {
    var keyPrefix string
    switch rl.mode {
    case "event":
        keyPrefix = "rl:event"
    case "api":
        keyPrefix = "rl:api"
    default:
        keyPrefix = "rl:default"
    }

    return func(c *gin.Context) {
        ip := c.ClientIP()
        key := keyPrefix + ":" + ip

        ctx := context.Background()
        count, err := rl.rdb.Incr(ctx, key).Result()
        if err != nil {
            c.AbortWithError(500, err)
            return
        }
        if count == 1 {
            rl.rdb.Expire(ctx, key, time.Minute)
        }

        limit := rl.getLimit()
        if count > limit {
            c.JSON(429, gin.H{
                "code":    429,
                "error":   "rate_limit_exceeded",
                "message": "请求过于频繁，请稍后重试",
                "retry_after": count - limit,
            })
            c.Abort()
            return
        }

        c.Header("X-RateLimit-Limit", fmt.Sprintf("%d", limit))
        c.Header("X-RateLimit-Remaining", fmt.Sprintf("%d", limit-count))
        c.Next()
    }
}

func (rl *RateLimiter) getLimit() int64 {
    switch rl.mode {
    case "event":
        return 100  // 事件上报：100 次/分钟/IP
    case "api":
        return 60   // API 调用：60 次/分钟/IP
    default:
        return 30
    }
}
```

### 3.5 异步写入模块

```go
// internal/writer/clickhouse.go
package writer

import (
    "context"
    "encoding/json"
    "fmt"

    "github.com/brainspark/gateway/internal/config"
    "github.com/ClickHouse/clickhouse-go/v2"
    "github.com/ClickHouse/clickhouse-go/v2/lib/driver"
    "github.com/google/uuid"
)

type ClickHouseWriter struct {
    conn   driver.Conn
    ch     chan AssessmentResult
    logger *Logger
}

var batchSize = 1000
var batchTimeout = 2 * time.Second

func NewClickHouseWriter(cfg config.ClickHouseConfig) (*ClickHouseWriter, error) {
    conn, err := clickhouse.Open(&clickhouse.Options{
        Addr: []string{cfg.Addr},
        Auth: clickhouse.Auth{
            Database: cfg.Database,
            Username: cfg.Username,
            Password: cfg.Password,
        },
        MaxOpenConns: 10,
        DialTimeout:  5 * time.Second,
    })
    if err != nil {
        return nil, err
    }
    return &ClickHouseWriter{conn: conn, ch: make(chan AssessmentResult, 10000)}, nil
}

func (w *ClickHouseWriter) Start(ctx context.Context) {
    go w.flushLoop(ctx)
}

func (w *ClickHouseWriter) Submit(result AssessmentResult) {
    select {
    case w.ch <- result:
    default:
        w.logger.Warn("event_channel_full", "dropped_result", result.EventID)
    }
}

func (w *ClickHouseWriter) flushLoop(ctx context.Context) {
    ticker := time.NewTicker(batchTimeout)
    defer ticker.Stop()

    var batch []AssessmentResult

    for {
        select {
        case <-ctx.Done():
            w.flushBatch(batch)
            return
        case r, ok := <-w.ch:
            if !ok {
                w.flushBatch(batch)
                return
            }
            batch = append(batch, r)
            if len(batch) >= batchSize {
                w.flushBatch(batch)
                batch = nil
            }
        case <-ticker.C:
            if len(batch) > 0 {
                w.flushBatch(batch)
                batch = nil
            }
        }
    }
}

func (w *ClickHouseWriter) flushBatch(batch []AssessmentResult) {
    if len(batch) == 0 {
        return
    }

    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    batch, err := w.conn.Batch(ctx)
    if err != nil {
        // retry logic / dead letter queue
        return
    }
    _ = batch.Get()
}

type AssessmentResult struct {
    EventID    string                 `json:"event_id"`
    UserID     int64                  `json:"user_id"`
    TaskID     string                 `json:"task_id"`
    StartAt    time.Time              `json:"start_at"`
    EndAt      time.Time              `json:"end_at"`
    ScoreData  map[string]interface{} `json:"score_data"`
    SessionID  string                 `json:"session_id"`
    RequestID  string                 `json:"request_id"`
    Status     string                 `json:"status"`
}
```

## 4. WebSocket 网关设计

### 4.1 Hub 架构

```go
// internal/websocket/hub.go
package websocket

import (
    "encoding/json"
    "sync"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool {
        return true // Nginx 已在反向代理层做 CORS 处理
    },
}

type Message struct {
    Type      string      `json:"type"`
    Data      interface{} `json:"data"`
    Timestamp time.Time   `json:"timestamp"`
    ClientID  string      `json:"client_id"`
}

type Hub struct {
    clients    map[string]*Client
    register   chan *Client
    unregister chan *Client
    broadcast  chan []byte
    mu         sync.RWMutex
}

func NewHub() *Hub {
    return &Hub{
        clients:    make(map[string]*Client),
        register:   make(chan *Client, 100),
        unregister: make(chan *Client, 100),
        broadcast:  make(chan []byte, 1000),
    }
}

func (h *Hub) Run() {
    for {
        select {
        case client := <-h.register:
            h.mu.Lock()
            h.clients[client.ID] = client
            h.mu.Unlock()
        case client := <-h.unregister:
            h.mu.Lock()
            if _, ok := h.clients[client.ID]; ok {
                delete(h.clients, client.ID)
                close(client.Send)
            }
            h.mu.Unlock()
        case message := <-h.broadcast:
            h.mu.RLock()
            for _, client := range h.clients {
                select {
                case client.Send <- message:
                default:
                    close(client.Send)
                    delete(h.clients, client.ID)
                }
            }
            h.mu.RUnlock()
        }
    }
}

func (h *Hub) Count() int {
    h.mu.RLock()
    defer h.mu.RUnlock()
    return len(h.clients)
}

func (h *Hub) HTTPHandler() http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        conn, err := upgrader.Upgrade(w, r, nil)
        if err != nil {
            return
        }

        client := NewClient(h, conn)
        h.register <- client
        client.ReadPump()
    })
}

// Stats 返回 WebSocket 统计信息（供 /ws/stats 端点使用）
func (h *Hub) Stats() HubStats {
    h.mu.RLock()
    defer h.mu.RUnlock()
    return HubStats{
        Count:   len(h.clients),
        MaxConn: maxConnPerUser,
    }
}
```

## 5. 统一响应格式

```go
// internal/model/response.go
package model

type Response struct {
    Code    int         `json:"code"`
    Data    interface{} `json:"data"`
    Message string      `json:"message"`
    RequestID string    `json:"request_id,omitempty"`
}

func Success(data interface{}, msg string, reqID string) Response {
    return Response{
        Code: 200,
        Data: data,
        Message: msg,
        RequestID: reqID,
    }
}

func Error(code int, msg string, reqID string) Response {
    return Response{
        Code: code,
        Message: msg,
        RequestID: reqID,
    }
}
```

## 6. 部署架构

### 6.1 Docker Compose

```yaml
version: '3.8'
services:
  nginx:
    image: nginx:1.25
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./conf.d:/etc/nginx/conf.d
    depends_on:
      - api-gateway
      - ai-service
      - student-web
      - parent-web
      - teacher-web
      - operator-web

  api-gateway:
    build: ./apps/backend-gateway
    ports:
      - "8081:8081"  # HTTP
      - "8082:8082"  # WebSocket
    environment:
      - REDIS_ADDR=redis:6379
      - CLICKHOUSE_ADDR=clickhouse:9000

  ai-service:
    build: ./apps/ai-service
    ports:
      - "8000:8000"
```

## 7. 性能指标

| 指标 | 目标 |
|------|------|
| HTTP 网关 QPS | 10,000+ |
| WebSocket 并发连接 | 50,000+ |
| 事件写入延迟（P95） | < 200ms |
| API 平均响应时间 | < 50ms |

## 8. 监控端点

| 端点 | 功能 |
|------|------|
| `GET /api/v1/health` | 基础健康检查 |
| `GET /api/v1/metrics` | Prometheus 指标 |
| `GET /ws/stats` | WebSocket 连接统计 |