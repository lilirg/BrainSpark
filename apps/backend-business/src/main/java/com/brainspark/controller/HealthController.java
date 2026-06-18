package com.brainspark.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.sql.DataSource;
import java.sql.Connection;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequiredArgsConstructor
public class HealthController {

    private final DataSource dataSource;
    private final StringRedisTemplate redisTemplate;

    @GetMapping("/api/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> result = new HashMap<>();
        result.put("status", "UP");
        result.put("service", "brainspark-business");
        result.put("timestamp", LocalDateTime.now().toString());

        // 数据库健康检查
        Map<String, Object> dbHealth = new HashMap<>();
        try (Connection conn = dataSource.getConnection()) {
            dbHealth.put("status", "UP");
            dbHealth.put("database", conn.getMetaData().getDatabaseProductName());
            dbHealth.put("version", conn.getMetaData().getDatabaseProductVersion());
        } catch (Exception e) {
            dbHealth.put("status", "DOWN");
            dbHealth.put("error", e.getMessage());
            result.put("status", "DEGRADED");
        }
        result.put("database", dbHealth);

        // Redis 健康检查
        Map<String, Object> redisHealth = new HashMap<>();
        try {
            String pong = redisTemplate.getConnectionFactory().getConnection().ping();
            redisHealth.put("status", "UP");
            redisHealth.put("ping", pong);
        } catch (Exception e) {
            redisHealth.put("status", "DOWN");
            redisHealth.put("error", e.getMessage());
            result.put("status", "DEGRADED");
        }
        result.put("redis", redisHealth);

        return ResponseEntity.ok(result);
    }

    @GetMapping("/api/metrics/prometheus")
    public ResponseEntity<Map<String, Object>> metrics() {
        Map<String, Object> metrics = new HashMap<>();
        metrics.put("service", "brainspark-business");
        metrics.put("timestamp", LocalDateTime.now().toString());
        metrics.put("uptime", System.currentTimeMillis());
        metrics.put("memory", Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory());
        metrics.put("totalMemory", Runtime.getRuntime().totalMemory());
        metrics.put("freeMemory", Runtime.getRuntime().freeMemory());
        metrics.put("availableProcessors", Runtime.getRuntime().availableProcessors());
        return ResponseEntity.ok(metrics);
    }
}