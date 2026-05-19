package main

import (
	"log"
	"net/http/proxy"
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