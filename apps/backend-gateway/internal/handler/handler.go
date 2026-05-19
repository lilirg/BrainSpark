package handler

import (
	"log"
	"time"

	"github.com/brainspark/gateway/internal/model"
	"github.com/brainspark/gateway/internal/writer"

	"github.com/gin-gonic/gin"
)

// HealthCheck returns the health status of the gateway
func HealthCheck(c *gin.Context) {
	status := model.HealthStatus{
		Status:    "ok",
		Timestamp: time.Now().Format(time.RFC3339),
		Version:   "0.1.0",
	}
	c.JSON(200, status)
}

// ReportResults handles game assessment result submissions
func ReportResults(c *gin.Context) {
	var result model.AssessmentResult
	if err := c.ShouldBindJSON(&result); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	// Write to ClickHouse (async)
	go writer.WriteToClickHouse(result)

	// Fast response
	c.JSON(201, gin.H{
		"status":   "accepted",
		"event_id": result.EventID,
	})
}