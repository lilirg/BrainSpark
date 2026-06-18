package handler

import (
	"net/http"
	"sync"
	"time"

	"github.com/brainspark/gateway/internal/model"
	"github.com/brainspark/gateway/internal/writer"
	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true // 开发阶段允许所有来源
	},
}

type EventHandler struct {
	writer    *writer.EventWriter
	clients   map[string]*websocket.Conn
	clientsMu sync.RWMutex
}

func NewEventHandler(writer *writer.EventWriter) *EventHandler {
	return &EventHandler{
		writer:  writer,
		clients: make(map[string]*websocket.Conn),
	}
}

// POST /api/v1/events/batch - 批量事件采集
func (h *EventHandler) BatchEvents(c *gin.Context) {
	var req model.BatchEventRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"code":    400,
			"message": "请求格式错误: " + err.Error(),
		})
		return
	}

	if len(req.Events) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{
			"code":    400,
			"message": "事件列表不能为空",
		})
		return
	}

	// 设置创建时间
	now := time.Now()
	for i := range req.Events {
		req.Events[i].CreatedAt = now
	}

	// 异步写入 MongoDB
	go func() {
		if err := h.writer.WriteBatch(req.Events); err != nil {
			// 实际项目中应记录错误日志
			println("[EVENT] 批量事件写入失败:", err.Error())
		}
	}()

	c.JSON(http.StatusOK, gin.H{
		"code":    200,
		"message": "事件已接收",
		"data": gin.H{
			"count": len(req.Events),
		},
	})
}

// GET /api/v1/events/ws - WebSocket 事件连接
func (h *EventHandler) WebSocket(c *gin.Context) {
	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"code":    500,
			"message": "WebSocket 升级失败: " + err.Error(),
		})
		return
	}

	clientID := c.Query("clientId")
	if clientID == "" {
		clientID = c.ClientIP() + ":" + time.Now().String()
	}

	// 注册客户端
	h.clientsMu.Lock()
	h.clients[clientID] = conn
	h.clientsMu.Unlock()

	defer func() {
		h.clientsMu.Lock()
		delete(h.clients, clientID)
		h.clientsMu.Unlock()
		conn.Close()
	}()

	// 读取消息
	for {
		var msg model.WSMessage
		if err := conn.ReadJSON(&msg); err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseNormalClosure) {
				println("[WS] 连接异常关闭:", err.Error())
			}
			break
		}

		switch msg.Type {
		case "event":
			if msg.Event != nil {
				msg.Event.CreatedAt = time.Now()
				go func(e model.BehaviorEvent) {
					if err := h.writer.WriteSingle(e); err != nil {
						println("[WS] 事件写入失败:", err.Error())
						// 发送错误 ACK
						ack := model.WSMessage{
							Type:  "error",
							AckID: msg.AckID,
							Error: "事件写入失败",
						}
						conn.WriteJSON(ack)
						return
					}
					// 发送成功 ACK
					ack := model.WSMessage{
						Type:  "ack",
						AckID: msg.AckID,
					}
					conn.WriteJSON(ack)
				}(*msg.Event)
			}
		case "ping":
			pong := model.WSMessage{Type: "pong"}
			conn.WriteJSON(pong)
		}
	}
}