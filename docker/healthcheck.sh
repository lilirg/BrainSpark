#!/bin/bash
# BrainSpark 服务健康检查脚本

echo "=== BrainSpark 服务健康检查 ==="
echo ""

# 检查 Go 网关
echo "1. Go 网关 (localhost:8080)"
curl -s http://localhost:8080/api/health | python -m json.tool 2>/dev/null || echo "   ❌ 无法连接"

# 检查 Java 业务后端
echo ""
echo "2. Java 业务后端 (localhost:8081)"
curl -s http://localhost:8081/api/health | python -m json.tool 2>/dev/null || echo "   ❌ 无法连接"

# 检查 MySQL
echo ""
echo "3. MySQL (localhost:3306)"
mysqladmin ping -h localhost -u root -pbrainspark_dev 2>/dev/null && echo "   ✅ 连接正常" || echo "   ❌ 无法连接"

# 检查 Redis
echo ""
echo "4. Redis (localhost:6379)"
redis-cli -a brainspark_dev ping 2>/dev/null && echo "   ✅ 连接正常" || echo "   ❌ 无法连接"

# 检查 MongoDB
echo ""
echo "5. MongoDB (localhost:27017)"
mongosh --quiet --eval "db.runCommand({ping:1})" 2>/dev/null | grep -q "ok" && echo "   ✅ 连接正常" || echo "   ❌ 无法连接"

# 检查 ClickHouse
echo ""
echo "6. ClickHouse (localhost:8123)"
curl -s http://localhost:8123/ping 2>/dev/null | grep -q "Ok" && echo "   ✅ 连接正常" || echo "   ❌ 无法连接"

echo ""
echo "=== 检查完成 ==="