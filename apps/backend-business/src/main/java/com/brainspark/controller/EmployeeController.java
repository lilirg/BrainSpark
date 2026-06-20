package com.brainspark.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/v1/employee")
@RequiredArgsConstructor
@PreAuthorize("hasAnyRole('EMPLOYEE', 'MANAGER')")
public class EmployeeController {

    @GetMapping("/dashboard/stats")
    public ResponseEntity<Map<String, Object>> getDashboardStats() {
        return ResponseEntity.ok(Map.of(
            "pendingTasks", 15,
            "todayAppointments", 8,
            "newMessages", 23,
            "completedToday", 12
        ));
    }

    @GetMapping("/dashboard/todos")
    public ResponseEntity<List<Map<String, Object>>> getTodos() {
        return ResponseEntity.ok(List.of(
            Map.of("id", 1, "title", "审核家长绑定申请", "priority", "HIGH", "deadline", "2026-06-20"),
            Map.of("id", 2, "title", "处理学生档案更新", "priority", "MEDIUM", "deadline", "2026-06-21")
        ));
    }

    @GetMapping("/parents")
    public ResponseEntity<List<Map<String, Object>>> getParents() {
        return ResponseEntity.ok(List.of(
            Map.of("id", 1, "name", "张先生", "children", 2, "status", "ACTIVE"),
            Map.of("id", 2, "name", "李女士", "children", 1, "status", "PENDING")
        ));
    }

    @PostMapping("/parents/{id}/guidance")
    public ResponseEntity<Map<String, String>> sendGuidance(
            @PathVariable Long id, @RequestBody Map<String, String> body) {
        return ResponseEntity.ok(Map.of("message", "指导建议已发送"));
    }

    @PostMapping("/messages/send")
    public ResponseEntity<Map<String, String>> sendMessage(@RequestBody Map<String, Object> body) {
        return ResponseEntity.ok(Map.of("message", "消息已发送"));
    }
}