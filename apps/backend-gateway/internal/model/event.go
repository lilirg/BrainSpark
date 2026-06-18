package model

import "time"

// 行为事件
type BehaviorEvent struct {
	ID         string         `json:"id" bson:"_id"`
	SessionID  string         `json:"sessionId" bson:"session_id"`
	StudentID  string         `json:"studentId" bson:"student_id"`
	Type       string         `json:"type" bson:"type"`
	Timestamp  int64          `json:"timestamp" bson:"timestamp"` // 微秒级时间戳
	Data       map[string]any `json:"data,omitempty" bson:"data,omitempty"`
	DeviceInfo *DeviceInfo    `json:"deviceInfo,omitempty" bson:"device_info,omitempty"`
	CreatedAt  time.Time      `json:"createdAt" bson:"created_at"`
}

// 设备信息
type DeviceInfo struct {
	UserAgent        string `json:"userAgent" bson:"user_agent"`
	ScreenResolution string `json:"screenResolution" bson:"screen_resolution"`
	DeviceType       string `json:"deviceType" bson:"device_type"`
	Browser          string `json:"browser" bson:"browser"`
	OS               string `json:"os" bson:"os"`
}

// 批量事件请求
type BatchEventRequest struct {
	Events []BehaviorEvent `json:"events" binding:"required"`
}

// WebSocket 消息
type WSMessage struct {
	Type  string         `json:"type"`
	Event *BehaviorEvent `json:"event,omitempty"`
	AckID string         `json:"ackId,omitempty"`
	Error string         `json:"error,omitempty"`
}