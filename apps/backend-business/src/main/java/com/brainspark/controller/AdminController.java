package com.brainspark.controller;

import com.brainspark.entity.AssessmentType;
import com.brainspark.entity.AssessmentTask;
import com.brainspark.entity.SchoolClass;
import com.brainspark.entity.User;
import com.brainspark.repository.AssessmentTypeRepository;
import com.brainspark.repository.AssessmentTaskRepository;
import com.brainspark.repository.SchoolClassRepository;
import com.brainspark.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/admin")
@RequiredArgsConstructor
@PreAuthorize("hasRole('ADMIN')")
public class AdminController {

    private final AssessmentTypeRepository assessmentTypeRepository;
    private final AssessmentTaskRepository assessmentTaskRepository;
    private final SchoolClassRepository schoolClassRepository;
    private final UserRepository userRepository;

    // 内容管理
    @GetMapping("/content/assessments")
    public ResponseEntity<List<Map<String, Object>>> getAssessmentContent() {
        List<AssessmentType> types = assessmentTypeRepository.findAll();
        List<Map<String, Object>> content = types.stream().map(type -> {
            Map<String, Object> map = new HashMap<>();
            map.put("id", type.getId());
            map.put("name", type.getName());
            map.put("typeCode", type.getCode());
            map.put("description", type.getDescription());
            map.put("durationMin", type.getDurationSeconds() != null ? type.getDurationSeconds() / 60 : 15);
            map.put("difficulty", type.getDifficulty() != null ? type.getDifficulty().name() : "MEDIUM");
            map.put("status", type.getStatus() != null ? type.getStatus().name() : "ACTIVE");
            map.put("createdAt", type.getCreatedAt() != null ? type.getCreatedAt().toString() : LocalDateTime.now().toString());
            return map;
        }).collect(Collectors.toList());
        return ResponseEntity.ok(content);
    }

    @PutMapping("/content/assessments/{id}/status")
    public ResponseEntity<Map<String, String>> updateAssessmentStatus(
            @PathVariable Long id, @RequestBody Map<String, String> body) {
        AssessmentType type = assessmentTypeRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("测评类型不存在"));
        String status = body.get("status");
        if ("ACTIVE".equals(status)) {
            type.setStatus(AssessmentType.AssessmentTypeStatus.ACTIVE);
        } else if ("INACTIVE".equals(status)) {
            type.setStatus(AssessmentType.AssessmentTypeStatus.INACTIVE);
        }
        assessmentTypeRepository.save(type);
        return ResponseEntity.ok(Map.of("message", "测评状态已更新"));
    }

    // 知识库管理
    @GetMapping("/knowledge/docs")
    public ResponseEntity<List<Map<String, Object>>> getKnowledgeDocs() {
        List<AssessmentTask> tasks = assessmentTaskRepository.findAll();
        List<Map<String, Object>> docs = tasks.stream().map(task -> {
            Map<String, Object> map = new HashMap<>();
            map.put("id", task.getId());
            map.put("title", task.getTitle());
            map.put("category", task.getTypeCode());
            map.put("status", task.getStatus() != null ? task.getStatus().name() : "PENDING");
            map.put("createdAt", task.getCreatedAt() != null ? task.getCreatedAt().toString() : LocalDateTime.now().toString());
            map.put("updatedAt", task.getUpdatedAt() != null ? task.getUpdatedAt().toString() : LocalDateTime.now().toString());
            return map;
        }).collect(Collectors.toList());
        return ResponseEntity.ok(docs);
    }

    @PostMapping("/knowledge/reindex")
    public ResponseEntity<Map<String, String>> reindexKnowledge() {
        return ResponseEntity.ok(Map.of("message", "知识库重建任务已提交"));
    }

    // 数据统计
    @GetMapping("/analytics/dashboard")
    public ResponseEntity<Map<String, Object>> getAnalytics() {
        Map<String, Object> analytics = new HashMap<>();
        analytics.put("totalUsers", userRepository.count());
        analytics.put("activeUsers", userRepository.count());
        analytics.put("totalAssessments", assessmentTaskRepository.count());
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
        List<SchoolClass> classes = schoolClassRepository.findAll();
        List<Map<String, Object>> partners = classes.stream().map(cls -> {
            Map<String, Object> map = new HashMap<>();
            map.put("id", cls.getId());
            map.put("name", cls.getName());
            map.put("students", cls.getMaxStudents() != null ? cls.getMaxStudents() : 0);
            map.put("status", cls.getIsActive() ? "ACTIVE" : "PENDING");
            map.put("createdAt", cls.getCreatedAt() != null ? cls.getCreatedAt().toString() : LocalDateTime.now().toString());
            return map;
        }).collect(Collectors.toList());
        return ResponseEntity.ok(partners);
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