package com.brainspark.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;

@RestController
@RequestMapping("/api/v1/admin")
@RequiredArgsConstructor
@PreAuthorize("hasRole('ADMIN')")
public class AdminController {

    // 内容管理
    @GetMapping("/content/assessments")
    public ResponseEntity<List<Map<String, Object>>> getAssessmentContent() {
        List<Map<String, Object>> content = List.of(
            Map.of("id", 1, "name", "舒尔特方格", "type", "SCHULTER", "status", "ACTIVE"),
            Map.of("id", 2, "name", "数字广度", "type", "DIGITAL_SPAN", "status", "ACTIVE"),
            Map.of("id", 3, "name", "图形推理", "type", "PATTERN_REASONING", "status", "INACTIVE")
        );
        return ResponseEntity.ok(content);
    }

    @PutMapping("/content/assessments/{id}/status")
    public ResponseEntity<Map<String, String>> updateAssessmentStatus(
            @PathVariable Long id, @RequestBody Map<String, String> body) {
        return ResponseEntity.ok(Map.of("message", "测评状态已更新"));
    }

    // 知识库管理
    @GetMapping("/knowledge/docs")
    public ResponseEntity<List<Map<String, Object>>> getKnowledgeDocs() {
        return ResponseEntity.ok(List.of(
            Map.of("id", 1, "title", "注意力训练指南", "status", "INDEXED"),
            Map.of("id", 2, "title", "记忆力提升方法", "status", "PENDING")
        ));
    }

    @PostMapping("/knowledge/reindex")
    public ResponseEntity<Map<String, String>> reindexKnowledge() {
        return ResponseEntity.ok(Map.of("message", "知识库重建任务已提交"));
    }

    // 数据统计
    @GetMapping("/analytics/dashboard")
    public ResponseEntity<Map<String, Object>> getAnalytics() {
        Map<String, Object> analytics = new HashMap<>();
        analytics.put("totalUsers", 12580);
        analytics.put("activeUsers", 3842);
        analytics.put("totalAssessments", 45678);
        analytics.put("completionRate", 87.5);
        analytics.put("dailyActiveUsers", 1256);
        analytics.put("newUsersToday", 89);
        analytics.put("revenue", 158000.0);
        analytics.put("userGrowth", Map.of(
            "daily", 2.3, "weekly", 15.8, "monthly", 45.2
        ));
        return ResponseEntity.ok(analytics);
    }

    // 机构合作管理
    @GetMapping("/partners")
    public ResponseEntity<List<Map<String, Object>>> getPartners() {
        return ResponseEntity.ok(List.of(
            Map.of("id", 1, "name", "阳光小学", "status", "ACTIVE", "students", 1200),
            Map.of("id", 2, "name", "星星幼儿园", "status", "PENDING", "students", 300)
        ));
    }

    @PostMapping("/partners")
    public ResponseEntity<Map<String, String>> createPartner(@RequestBody Map<String, String> body) {
        return ResponseEntity.ok(Map.of("message", "合作机构已创建"));
    }

    // 通知管理
    @PostMapping("/notifications")
    public ResponseEntity<Map<String, String>> sendNotification(@RequestBody Map<String, Object> body) {
        return ResponseEntity.ok(Map.of("message", "通知已发送"));
    }
}