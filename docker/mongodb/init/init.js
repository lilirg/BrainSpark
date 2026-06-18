// BrainSpark MongoDB 初始化脚本
// 基于 docs/architecture/data-model.md 定义

// 切换到 brainspark_events 数据库
db = db.getSiblingDB('brainspark_events');

// 行为事件集合 - 使用时序集合
db.createCollection('event_records', {
  timeseries: {
    timeField: 'created_at',
    metaField: 'metadata',
    granularity: 'seconds'
  }
});

// 创建索引
db.event_records.createIndex({ 'user_id': 1, 'session_id': 1 });
db.event_records.createIndex({ 'created_at': -1 });
db.event_records.createIndex({ 'user_id': 1, 'created_at': -1 });
db.event_records.createIndex({ 'session_id': 1 });
db.event_records.createIndex({ 'event_type': 1 });
db.event_records.createIndex({ 'created_at': 1 }, { expireAfterSeconds: 2592000 }); // 30天 TTL

// 设备信息集合
db.createCollection('device_info');
db.device_info.createIndex({ 'user_id': 1 });
db.device_info.createIndex({ 'device_type': 1 });
db.device_info.createIndex({ 'session_id': 1 });

// 创建 brainspark 数据库（用于应用数据）
db2 = db.getSiblingDB('brainspark');

// 会话缓存集合
db2.createCollection('sessions');
db2.sessions.createIndex({ 'user_id': 1 }, { expireAfterSeconds: 2592000 }); // 30天 TTL
db2.sessions.createIndex({ 'expires_at': 1 }, { expireAfterSeconds: 0 });

print('MongoDB 初始化完成');
print('  - 数据库: brainspark_events');
print('    - 集合: event_records (时序集合, 30天 TTL)');
print('    - 集合: device_info');
print('  - 数据库: brainspark');
print('    - 集合: sessions (30天 TTL)');