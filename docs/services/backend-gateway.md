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

## 2. Nginx 反向代理设计（目标架构 — 规划中）

> **当前实现**: 当前网关为单端口直接暴露，未使用 Nginx 反向代理。以下 Nginx 配置为生产环境建议添加的目标架构设计。

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
    server_name brainspark.example.com;

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
├── main.go                      # 入口（当前实现：单端口 :8081）
├── internal/
│   ├── handler/                 # 路由处理
│   │   ├── handler.go           # 游戏结果上报 + 健康检查
│   │   └── ...                  # （未来可扩展：event.go, ws.go, health.go）
│   ├── middleware/              # 中间件（全部在 middleware.go 中）
│   │   ├── middleware.go        # CORS + 内存限流 + RequestID
│   │   └── ...                  # （未来可扩展：request_id.go, rate_limiter.go, jwt_auth.go 等独立文件）
│   ├── model/                   # 数据模型
│   │   ├── event.go             # 行为事件模型 + 健康状态模型
│   │   └── ...                  # （未来可扩展：assessment.go, response.go）
│   ├── writer/                  # 异步写入
│   │   ├── writer.go            # ClickHouse 直接写入（当前实现）
│   │   └── ...                  # （未来可扩展：clickhouse.go, mongo.go, redis.go 等独立文件）
│   ├── websocket/               # WebSocket 模块（规划中）
│   │   └── ...                  # （未来可扩展：manager.go, hub.go, client.go）
│   └── proxy/                   # 正向代理（规划中）
│       └── ...                  # （未来可扩展：router.go）
├── go.mod
└── go.sum
```

### 3.2 入口设计

#### 当前实现

入口在根目录 [`main.go`](apps/backend-gateway/main.go)，单端口 `:8081`，使用 Gin 默认路由。

```go
// apps/backend-gateway/main.go（当前实现）
package main

import (
    "log"
    "time"

    "github.com/brainspark/gateway/internal/handler"
    "github.com/brainspark/gateway/internal/middleware"

    "github.com/gin-contrib/cors"
    "github.com/gin-gonic/gin"
)

func main() {
    // 初始化路由
    r := gin.Default()

    // 中间件
    r.Use(middleware.CORS())
    r.Use(middleware.RateLimiter())
    r.Use(middleware.RequestID())

    // API 路由组
    api := r.Group("/api/v1")
    {
        // 游戏结果上报网关
        api.POST("/assessment/results", handler.ReportResults)
        // 健康检查
        api.GET("/health", handler.HealthCheck)
    }

    // 启动服务
    log.Println("BrainSpark Gateway starting on :8081")
    if err := r.Run(":8081"); err != nil {
        log.Fatal("Failed to start gateway:", err)
    }
}
```

#### 目标架构（规划中）

以下 [`cmd/server/main.go`](apps/backend-gateway/cmd/server/main.go) 为未来多端口架构的目标设计，支持 HTTP 网关（`:8081`）和 WebSocket 网关（`:8082`）分离启动。
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

#### 当前实现

使用时间戳生成 Request ID，实现在 [`middleware.go:55`](apps/backend-gateway/internal/middleware/middleware.go:55)。

```go
// internal/middleware/middleware.go（当前实现）
func RequestID() gin.HandlerFunc {
    return func(c *gin.Context) {
        id := generateID()
        c.Header("X-Request-ID", id)
        c.Next()
    }
}

func generateID() string {
    return time.Now().Format("20060102150405") + "g"
}
```

> **说明**: 当前使用 `time.Now().Format("20060102150405") + "g"` 生成 Request ID，格式为时间戳字符串 + 后缀字符。未来可替换为 UUID 生成。

#### 目标架构（规划中）

以下为使用 UUID 的 Request ID 实现，将独立为 [`internal/middleware/request_id.go`](apps/backend-gateway/internal/middleware/request_id.go)。

### 3.4 限流中间件

#### 当前实现

使用内存 `map[string]int` 实现，每分钟每 IP 100 次，实现在 [`middleware.go:27`](apps/backend-gateway/internal/middleware/middleware.go:27)。

```go
// internal/middleware/middleware.go（当前实现）
// RateLimiter is a simple in-memory rate limiter
func RateLimiter() gin.HandlerFunc {
    requests := make(map[string]int)
    limit := 100 // requests per minute
    window := time.Minute

    go func() {
        ticker := time.NewTicker(window)
        defer ticker.Stop()
        for range ticker.C {
            for k := range requests {
                delete(requests, k)
            }
        }
    }()

    return func(c *gin.Context) {
        ip := c.ClientIP()
        if requests[ip] > limit {
            c.JSON(http.StatusTooManyRequests, gin.H{"error": "Rate limit exceeded"})
            c.Abort()
            return
        }
        requests[ip]++
        c.Next()
    }
}
```

> **说明**: 当前为简化版内存实现，每分钟重置计数器。未来可替换为 Redis 分布式限流以支持多实例部署。

#### 目标架构（规划中）

以下为使用 Redis 的分布式限流实现，将独立为 [`internal/middleware/rate_limiter.go`](apps/backend-gateway/internal/middleware/rate_limiter.go)。

### 3.5 异步写入模块

#### 当前实现

直接写入 ClickHouse（模拟实现），实现在 [`writer.go`](apps/backend-gateway/internal/writer/writer.go)。

```go
// internal/writer/writer.go（当前实现）
package writer

import (
    "log"
    "time"

    "github.com/brainspark/gateway/internal/model"
)

// WriteToClickHouse writes assessment results to ClickHouse asynchronously
func WriteToClickHouse(result model.AssessmentResult) {
    // Simulate async write to ClickHouse
    // In production, use the ClickHouse Go driver
    log.Printf("Writing result: student=%s game=%s score=%.2f",
        result.StudentID, result.GameType, result.Score)

    // Buffer batch writes for better throughput
    time.Sleep(100 * time.Millisecond)
}
```

> **说明**: 当前为模拟写入，直接调用 ClickHouse 写入函数。未来可扩展为通过 Kafka 消息队列缓冲写入，以提升吞吐量和可靠性。

#### 目标架构（规划中）

以下为使用 ClickHouse 批量写入 + Kafka 消息队列的完整实现，将独立为 [`internal/writer/clickhouse.go`](apps/backend-gateway/internal/writer/clickhouse.go) 和 [`internal/writer/kafka.go`](apps/backend-gateway/internal/writer/kafka.go)。

## 4. WebSocket 网关设计（规划中）

> **当前实现**: 当前网关无 WebSocket 实现。以下为未来规划中的 WebSocket Hub 架构设计。

### 4.1 Hub 架构

```go
// internal/websocket/hub.go（目标架构 — 规划中）
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

## 5. 统一响应格式（目标架构 — 规划中）

> **当前实现**: 当前网关直接返回 `gin.H` 格式的 JSON 响应，未使用统一的 Response 结构体。以下为未来规划的统一响应格式。

```go
// internal/model/response.go（目标架构 — 规划中）
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

### 6.1 Docker Compose（目标架构 — 规划中）

> **当前实现**: 当前网关为单端口 `:8081` 直接运行，未使用 Docker Compose 编排。以下为未来生产环境部署的目标架构。

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
      - "8082:8082"  # WebSocket（规划中）
    environment:
      - CLICKHOUSE_ADDR=clickhouse:9000

  ai-service:
    build: ./apps/ai-service
    ports:
      - "8000:8000"
```

## 7. 性能指标

| 指标 | 当前实现 | 目标 |
|------|----------|------|
| HTTP 网关 QPS | 单实例 ~1,000+ | 10,000+ |
| WebSocket 并发连接 | 未实现 | 50,000+ |
| 事件写入延迟（P95） | ~100ms（模拟写入） | < 200ms |
| API 平均响应时间 | < 10ms | < 50ms |

## 8. 监控端点

| 端点 | 功能 | 状态 |
|------|------|------|
| `GET /api/v1/health` | 基础健康检查 | ✅ 已实现 |
| `GET /api/v1/metrics` | Prometheus 指标 | ❌ 规划中 |
| `GET /ws/stats` | WebSocket 连接统计 | ❌ 规划中 |