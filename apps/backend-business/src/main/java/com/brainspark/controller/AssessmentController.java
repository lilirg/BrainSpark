package com.brainspark.controller;

import com.brainspark.dto.AssessmentTaskRequest;
import com.brainspark.dto.AssessmentTaskResponse;
import com.brainspark.dto.AssessmentTypeResponse;
import com.brainspark.entity.AssessmentResult;
import com.brainspark.entity.AssessmentSession;
import com.brainspark.entity.AssessmentTask;
import com.brainspark.service.AssessmentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/assessments")
@RequiredArgsConstructor
public class AssessmentController {

    private final AssessmentService assessmentService;

    // ========== 测评类型 ==========

    @GetMapping("/types")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'EMPLOYEE', 'TEACHER')")
    public ResponseEntity<Page<AssessmentTypeResponse>> getAssessmentTypes(
            @RequestParam(required = false) String category,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "createdAt") String sortBy,
            @RequestParam(defaultValue = "desc") String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("asc") ?
                Sort.by(sortBy).ascending() : Sort.by(sortBy).descending();
        PageRequest pageable = PageRequest.of(page, size, sort);
        return ResponseEntity.ok(assessmentService.getAssessmentTypes(category, status, pageable));
    }

    @GetMapping("/types/{id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'EMPLOYEE', 'TEACHER')")
    public ResponseEntity<AssessmentTypeResponse> getAssessmentType(@PathVariable Long id) {
        return ResponseEntity.ok(assessmentService.getAssessmentType(id));
    }

    @GetMapping("/types/by-code/{code}")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'EMPLOYEE', 'TEACHER')")
    public ResponseEntity<AssessmentTypeResponse> getAssessmentTypeByCode(@PathVariable String code) {
        return ResponseEntity.ok(assessmentService.getAssessmentTypeByCode(code));
    }

    // ========== 测评任务 ==========

    @GetMapping("/tasks")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'EMPLOYEE', 'TEACHER')")
    public ResponseEntity<Page<AssessmentTaskResponse>> getTasks(
            @RequestParam(required = false) Long classId,
            @RequestParam(required = false) String typeCode,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "createdAt") String sortBy,
            @RequestParam(defaultValue = "desc") String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("asc") ?
                Sort.by(sortBy).ascending() : Sort.by(sortBy).descending();
        PageRequest pageable = PageRequest.of(page, size, sort);
        return ResponseEntity.ok(assessmentService.getTasks(classId, typeCode, status, pageable));
    }

    @GetMapping("/tasks/{id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'EMPLOYEE', 'TEACHER')")
    public ResponseEntity<AssessmentTaskResponse> getTask(@PathVariable Long id) {
        return ResponseEntity.ok(assessmentService.getTask(id));
    }

    @PostMapping("/tasks")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'EMPLOYEE', 'TEACHER')")
    public ResponseEntity<AssessmentTaskResponse> createTask(@Valid @RequestBody AssessmentTaskRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(assessmentService.createTask(request));
    }

    @PutMapping("/tasks/{id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'EMPLOYEE', 'TEACHER')")
    public ResponseEntity<AssessmentTaskResponse> updateTask(
            @PathVariable Long id,
            @Valid @RequestBody AssessmentTaskRequest request) {
        return ResponseEntity.ok(assessmentService.updateTask(id, request));
    }

    @DeleteMapping("/tasks/{id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')")
    public ResponseEntity<Map<String, String>> deleteTask(@PathVariable Long id) {
        assessmentService.deleteTask(id);
        return ResponseEntity.ok(Map.of("message", "测评任务已删除"));
    }

    @PatchMapping("/tasks/{id}/status")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'EMPLOYEE', 'TEACHER')")
    public ResponseEntity<Map<String, String>> updateTaskStatus(
            @PathVariable Long id,
            @RequestBody Map<String, String> body) {
        AssessmentTask.TaskStatus status = AssessmentTask.TaskStatus.valueOf(body.get("status"));
        assessmentService.updateTaskStatus(id, status);
        return ResponseEntity.ok(Map.of("message", "任务状态已更新"));
    }

    @GetMapping("/tasks/today")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'EMPLOYEE', 'TEACHER')")
    public ResponseEntity<Map<String, Long>> getTodayTasks() {
        return ResponseEntity.ok(Map.of(
                "inProgress", assessmentService.getTodayTaskCount(),
                "completed", assessmentService.getCompletedAssessmentCount()
        ));
    }

    // ========== 测评会话 ==========

    @GetMapping("/sessions")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'EMPLOYEE', 'TEACHER')")
    public ResponseEntity<Page<AssessmentSession>> getSessions(
            @RequestParam(required = false) Long studentId,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        PageRequest pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        return ResponseEntity.ok(assessmentService.getSessions(studentId, status, pageable));
    }

    @GetMapping("/sessions/{sessionId}")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'EMPLOYEE', 'TEACHER')")
    public ResponseEntity<AssessmentSession> getSession(@PathVariable String sessionId) {
        return ResponseEntity.ok(assessmentService.getSession(sessionId));
    }

    // ========== 测评结果 ==========

    @GetMapping("/results")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'EMPLOYEE', 'TEACHER')")
    public ResponseEntity<Page<AssessmentResult>> getResults(
            @RequestParam(required = false) Long userId,
            @RequestParam(required = false) String typeCode,
            @RequestParam(required = false) String reportStatus,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        PageRequest pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        return ResponseEntity.ok(assessmentService.getResults(userId, typeCode, reportStatus, pageable));
    }

    @GetMapping("/results/{id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'EMPLOYEE', 'TEACHER')")
    public ResponseEntity<AssessmentResult> getResult(@PathVariable Long id) {
        return ResponseEntity.ok(assessmentService.getResult(id));
    }
}