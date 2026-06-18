.PHONY: help dev up down restart logs health

help: ## 显示帮助信息
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## 启动所有开发服务
	docker-compose up -d

up: ## 启动所有服务
	docker-compose up -d

down: ## 停止所有服务
	docker-compose down

restart: ## 重启所有服务
	docker-compose restart

logs: ## 查看服务日志
	docker-compose logs -f

health: ## 检查所有服务健康状态
	@echo "=== 服务健康状态 ==="
	@echo "Go 网关:    $$(curl -s http://localhost:8080/api/health | python -c 'import sys,json; print(json.load(sys.stdin).get(\"status\",\"unknown\"))' 2>/dev/null || echo '❌')"
	@echo "Java 后端:  $$(curl -s http://localhost:8081/api/health | python -c 'import sys,json; print(json.load(sys.stdin).get(\"status\",\"unknown\"))' 2>/dev/null || echo '❌')"
	@echo "MySQL:      $$(mysqladmin ping -h localhost -u root -pbrainspark_dev 2>/dev/null && echo '✅' || echo '❌')"
	@echo "Redis:      $$(redis-cli -a brainspark_dev ping 2>/dev/null && echo '✅' || echo '❌')"
	@echo "MongoDB:    $$(mongosh --quiet --eval 'db.runCommand({ping:1}).ok' 2>/dev/null && echo '✅' || echo '❌')"
	@echo "ClickHouse: $$(curl -s http://localhost:8123/ping 2>/dev/null && echo '✅' || echo '❌')"
	@echo "Prometheus: $$(curl -s http://localhost:9090/-/healthy 2>/dev/null && echo '✅' || echo '❌')"
	@echo "Grafana:    $$(curl -s http://localhost:3000/api/health 2>/dev/null && echo '✅' || echo '❌')"

db-init: ## 初始化数据库
	docker-compose exec mysql mysql -u root -pbrainspark_dev < docker/mysql/init/01-create-databases.sql
	docker-compose exec mysql mysql -u root -pbrainspark_dev users_schema < docker/mysql/init/02-create-users-tables.sql
	docker-compose exec mysql mysql -u root -pbrainspark_dev assessment_schema < docker/mysql/init/03-create-assessment-tables.sql
	docker-compose exec mysql mysql -u root -pbrainspark_dev mall_schema < docker/mysql/init/04-create-mall-tables.sql
	docker-compose exec mysql mysql -u root -pbrainspark_dev ai_schema < docker/mysql/init/05-create-ai-tables.sql
	docker-compose exec mysql mysql -u root -pbrainspark_dev < docker/mysql/init/06-seed-data.sql