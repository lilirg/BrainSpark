package writer

import (
	"context"
	"time"

	"github.com/brainspark/gateway/internal/model"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type EventWriter struct {
	collection *mongo.Collection
}

func NewEventWriter(mongoURI, dbName, collectionName string) (*EventWriter, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, err := mongo.Connect(ctx, options.Client().ApplyURI(mongoURI))
	if err != nil {
		return nil, err
	}

	// 验证连接
	if err := client.Ping(ctx, nil); err != nil {
		return nil, err
	}

	collection := client.Database(dbName).Collection(collectionName)
	return &EventWriter{collection: collection}, nil
}

// 批量写入事件
func (w *EventWriter) WriteBatch(events []model.BehaviorEvent) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	documents := make([]interface{}, len(events))
	for i, event := range events {
		documents[i] = event
	}

	_, err := w.collection.InsertMany(ctx, documents)
	return err
}

// 单条写入事件
func (w *EventWriter) WriteSingle(event model.BehaviorEvent) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	_, err := w.collection.InsertOne(ctx, event)
	return err
}