package model

import "time"

// AssessmentResult represents a game assessment result from student
type AssessmentResult struct {
	EventID     string    `json:"eventId"`
	StudentID   string    `json:"studentId"`
	GameType    string    `json:"gameType"`
	Score       float64   `json:"score"`
	StartTime   time.Time `json:"startTime"`
	EndTime     time.Time `json:"endTime"`
	Duration    int       `json:"duration"`
	TouchPoints int       `json:"touchPoints"`
	CorrectRate float64   `json:"correctRate"`
	Metadata    map[string]interface{} `json:"metadata"`
}

// HealthStatus represents the health check response
type HealthStatus struct {
	Status    string `json:"status"`
	Timestamp string `json:"timestamp"`
	Version   string `json:"version"`
}