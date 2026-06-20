package com.brainspark.dto;

import com.brainspark.entity.AssessmentTask.TaskStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AssessmentTaskResponse {
    private Long id;
    private Long orgId;
    private Long classId;
    private String title;
    private String description;
    private String typeCode;
    private String config;
    private Integer difficulty;
    private Integer durationMin;
    private LocalDateTime assignedAt;
    private LocalDateTime startAt;
    private LocalDateTime endAt;
    private Boolean isActive;
    private TaskStatus status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}