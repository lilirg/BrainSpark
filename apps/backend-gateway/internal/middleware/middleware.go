package middleware

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// CORS handles Cross-Origin Resource Sharing
func CORS() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}

		c.Next()
	}
}

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

// RequestID adds a unique ID to each request
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