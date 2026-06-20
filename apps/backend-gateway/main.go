package main

import (
	"os"
	"time"

	"github.com/brainspark/gateway/internal/handler"
	"github.com/brainspark/gateway/internal/middleware"
	"github.com/brainspark/gateway/internal/writer"
	"github.com/gin-gonic/gin"
	"golang.org/x/time/rate"
)

func main() {
	// 配置
	port := getEnv("PORT", "8080")
	mongoURI := getEnv("MONGO_URI", "mongodb://brainspark:brainspark_dev@localhost:27017")
	jwtSecret := getEnv("JWT_SECRET", "brainspark-jwt-secret-key-change-in-production")

	// 初始化 MongoDB 写入器
	eventWriter, err := writer.NewEventWriter(mongoURI, "brainspark_events", "event_records")
	if err != nil {
		panic("MongoDB 连接失败: " + err.Error())
	}

	// 初始化事件处理器
	eventHandler := handler.NewEventHandler(eventWriter)

	// 初始化限流器
	ipLimiter := middleware.NewIPRateLimiter(rate.Limit(500), 100) // IP 级别 500 QPS, burst 100

	// 创建 Gin 引擎
	r := gin.Default()

	// 全局中间件
	r.Use(middleware.CORS())
	r.Use(middleware.Logger())
	r.Use(middleware.RateLimit(ipLimiter))

	// 健康检查
	r.GET("/api/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":    "ok",
			"service":   "brainspark-gateway",
			"version":   "1.0.0",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
			"checks": gin.H{
				"mongodb": checkMongoDB(eventWriter),
			},
		})
	})

	// 公开路由
	public := r.Group("/api/v1")
	{
		public.POST("/events/batch", eventHandler.BatchEvents)
		public.GET("/events/ws", eventHandler.WebSocket)
	}

	// 需要认证的路由
	auth := r.Group("/api/v1")
	auth.Use(middleware.JWTAuth(jwtSecret))
	{
		// 后续添加需要认证的路由
	}

	// 启动服务
	r.Run(":" + port)
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// checkMongoDB 检查 MongoDB 连接状态
func checkMongoDB(writer *writer.EventWriter) gin.H {
	if err := writer.Ping(); err != nil {
		return gin.H{
			"status": "down",
			"error":  err.Error(),
		}
	}
	return gin.H{
		"status": "ok",
	}
}