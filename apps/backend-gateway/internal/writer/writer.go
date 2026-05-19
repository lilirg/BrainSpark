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