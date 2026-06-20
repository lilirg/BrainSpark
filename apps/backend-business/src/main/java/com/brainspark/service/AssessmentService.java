package com.brainspark.service;

import com.brainspark.dto.AssessmentTaskRequest;
import com.brainspark.dto.AssessmentTaskResponse;
import com.brainspark.dto.AssessmentTypeResponse;
import com.brainspark.entity.AssessmentResult;
import com.brainspark.entity.AssessmentSession;
import com.brainspark.entity.AssessmentTask;
import com.brainspark.entity.AssessmentType;
import com.brainspark.repository.AssessmentResultRepository;
import com.brainspark.repository.AssessmentSessionRepository;
import com.brainspark.repository.AssessmentTaskRepository;
import com.brainspark.repository.AssessmentTypeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class AssessmentService {

    private final AssessmentTypeRepository assessmentTypeRepository;
    private final AssessmentTaskRepository assessmentTaskRepository;
    private final AssessmentSessionRepository assessmentSessionRepository;
    private final AssessmentResultRepository assessmentResultRepository;

    // ========== 测评类型管理 ==========

    public Page<AssessmentTypeResponse> getAssessmentTypes(String category, String status, Pageable pageable) {
        Page<AssessmentType> types;
        if (category != null && status != null) {
            types = assessmentTypeRepository.findByCategory(
                    AssessmentType.Category.valueOf(category), pageable);
        } else if (status != null) {
            types = assessmentTypeRepository.findByStatus(
                    AssessmentType.Status.valueOf(status), pageable);
        } else {
            types = assessmentTypeRepository.findAll(pageable);
        }
        return types.map(this::toTypeResponse);
    }

    public AssessmentTypeResponse getAssessmentType(Long id) {
        AssessmentType type = assessmentTypeRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("测评类型不存在"));
        return toTypeResponse(type);
    }

    public AssessmentTypeResponse getAssessmentTypeByCode(String code) {
        AssessmentType type = assessmentTypeRepository.findByCode(code)
                .orElseThrow(() -> new RuntimeException("测评类型不存在: " + code));
        return toTypeResponse(type);
    }

    // ========== 测评任务管理 ==========

    public Page<AssessmentTaskResponse> getTasks(Long classId, String typeCode, String status, Pageable pageable) {
        Page<AssessmentTask> tasks;
        if (classId != null) {
            tasks = assessmentTaskRepository.findByClassId(classId, pageable);
        } else if (typeCode != null) {
            tasks = assessmentTaskRepository.findByTypeCode(typeCode, pageable);
        } else if (status != null) {
            tasks = assessmentTaskRepository.findByStatus(
                    AssessmentTask.TaskStatus.valueOf(status), pageable);
        } else {
            tasks = assessmentTaskRepository.findAll(pageable);
        }
        return tasks.map(this::toTaskResponse);
    }

    public AssessmentTaskResponse getTask(Long id) {
        AssessmentTask task = assessmentTaskRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("测评任务不存在"));
        return toTaskResponse(task);
    }

    @Transactional
    public AssessmentTaskResponse createTask(AssessmentTaskRequest request) {
        // 验证测评类型存在
        assessmentTypeRepository.findByCode(request.getTypeCode())
                .orElseThrow(() -> new RuntimeException("测评类型不存在: " + request.getTypeCode()));

        AssessmentTask task = new AssessmentTask();
        task.setTitle(request.getTitle());
        task.setDescription(request.getDescription());
        task.setTypeCode(request.getTypeCode());
        task.setConfig(request.getConfig());
        task.setDifficulty(request.getDifficulty());
        task.setDurationMin(request.getDurationMin());
        task.setClassId(request.getClassId());
        task.setStartAt(request.getStartAt());
        task.setEndAt(request.getEndAt());
        task.setAssignedAt(LocalDateTime.now());
        task.setStatus(AssessmentTask.TaskStatus.PENDING);
        task.setIsActive(true);

        task = assessmentTaskRepository.save(task);
        return toTaskResponse(task);
    }

    @Transactional
    public AssessmentTaskResponse updateTask(Long id, AssessmentTaskRequest request) {
        AssessmentTask task = assessmentTaskRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("测评任务不存在"));

        if (request.getTitle() != null) task.setTitle(request.getTitle());
        if (request.getDescription() != null) task.setDescription(request.getDescription());
        if (request.getTypeCode() != null) {
            assessmentTypeRepository.findByCode(request.getTypeCode())
                    .orElseThrow(() -> new RuntimeException("测评类型不存在: " + request.getTypeCode()));
            task.setTypeCode(request.getTypeCode());
        }
        if (request.getConfig() != null) task.setConfig(request.getConfig());
        if (request.getDifficulty() != null) task.setDifficulty(request.getDifficulty());
        if (request.getDurationMin() != null) task.setDurationMin(request.getDurationMin());
        if (request.getClassId() != null) task.setClassId(request.getClassId());
        if (request.getStartAt() != null) task.setStartAt(request.getStartAt());
        if (request.getEndAt() != null) task.setEndAt(request.getEndAt());

        task = assessmentTaskRepository.save(task);
        return toTaskResponse(task);
    }

    @Transactional
    public void deleteTask(Long id) {
        if (!assessmentTaskRepository.existsById(id)) {
            throw new RuntimeException("测评任务不存在");
        }
        assessmentTaskRepository.deleteById(id);
    }

    @Transactional
    public void updateTaskStatus(Long id, AssessmentTask.TaskStatus status) {
        AssessmentTask task = assessmentTaskRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("测评任务不存在"));
        task.setStatus(status);
        assessmentTaskRepository.save(task);
    }

    // ========== 测评会话管理 ==========

    public Page<AssessmentSession> getSessions(Long studentId, String status, Pageable pageable) {
        if (studentId != null) {
            return assessmentSessionRepository.findByStudentId(studentId, pageable);
        } else if (status != null) {
            return assessmentSessionRepository.findByStatus(
                    AssessmentSession.SessionStatus.valueOf(status), pageable);
        }
        return assessmentSessionRepository.findAll(pageable);
    }

    public AssessmentSession getSession(String sessionId) {
        return assessmentSessionRepository.findBySessionId(sessionId)
                .orElseThrow(() -> new RuntimeException("测评会话不存在"));
    }

    // ========== 测评结果管理 ==========

    public Page<AssessmentResult> getResults(Long userId, String typeCode, String reportStatus, Pageable pageable) {
        if (userId != null) {
            return assessmentResultRepository.findByUserId(userId, pageable);
        } else if (typeCode != null) {
            return assessmentResultRepository.findByTypeCode(typeCode, pageable);
        } else if (reportStatus != null) {
            return assessmentResultRepository.findByReportStatus(
                    AssessmentResult.ReportStatus.valueOf(reportStatus), pageable);
        }
        return assessmentResultRepository.findAll(pageable);
    }

    public AssessmentResult getResult(Long id) {
        return assessmentResultRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("测评结果不存在"));
    }

    // ========== 统计 ==========

    public long getTodayTaskCount() {
        return assessmentTaskRepository.countByStatus(AssessmentTask.TaskStatus.IN_PROGRESS);
    }

    public long getCompletedAssessmentCount() {
        return assessmentTaskRepository.countByStatus(AssessmentTask.TaskStatus.COMPLETED);
    }

    // ========== 转换方法 ==========

    private AssessmentTypeResponse toTypeResponse(AssessmentType type) {
        return AssessmentTypeResponse.builder()
                .id(type.getId())
                .code(type.getCode())
                .name(type.getName())
                .description(type.getDescription())
                .category(type.getCategory())
                .cognitiveDimension(type.getCognitiveDimension())
                .minAge(type.getMinAge())
                .maxAge(type.getMaxAge())
                .durationSeconds(type.getDurationSeconds())
                .version(type.getVersion())
                .config(type.getConfig())
                .isPublished(type.getIsPublished())
                .status(type.getStatus())
                .createdAt(type.getCreatedAt())
                .updatedAt(type.getUpdatedAt())
                .build();
    }

    private AssessmentTaskResponse toTaskResponse(AssessmentTask task) {
        return AssessmentTaskResponse.builder()
                .id(task.getId())
                .orgId(task.getOrgId())
                .classId(task.getClassId())
                .title(task.getTitle())
                .description(task.getDescription())
                .typeCode(task.getTypeCode())
                .config(task.getConfig())
                .difficulty(task.getDifficulty())
                .durationMin(task.getDurationMin())
                .assignedAt(task.getAssignedAt())
                .startAt(task.getStartAt())
                .endAt(task.getEndAt())
                .isActive(task.getIsActive())
                .status(task.getStatus())
                .createdAt(task.getCreatedAt())
                .updatedAt(task.getUpdatedAt())
                .build();
    }
}