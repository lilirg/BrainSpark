package com.brainspark.dto;

import com.brainspark.entity.AssessmentType.Category;
import com.brainspark.entity.AssessmentType.Status;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AssessmentTypeResponse {
    private Long id;
    private String code;
    private String name;
    private String description;
    private Category category;
    private String cognitiveDimension;
    private Integer minAge;
    private Integer maxAge;
    private Integer durationSeconds;
    private String version;
    private String config;
    private Boolean isPublished;
    private Status status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}