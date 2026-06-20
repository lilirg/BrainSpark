package com.brainspark.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.time.LocalDateTime;

@Data
public class AssessmentTaskRequest {
    @NotBlank(message = "标题不能为空")
    private String title;

    private String description;

    @NotBlank(message = "测评类型编码不能为空")
    private String typeCode;

    private String config;

    private Integer difficulty = 1;

    private Integer durationMin = 10;

    private Long classId;

    private LocalDateTime startAt;

    private LocalDateTime endAt;
}