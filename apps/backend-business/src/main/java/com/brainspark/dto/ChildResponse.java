package com.brainspark.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChildResponse {
    private Long id;
    private String name;
    private String studentCode;
    private String gender;
    private Integer age;
    private String grade;
    private String className;
    private String avatar;
    private Integer totalAssessments;
    private LocalDateTime lastAssessmentDate;
    private String status;
}