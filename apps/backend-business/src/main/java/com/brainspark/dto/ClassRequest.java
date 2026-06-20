package com.brainspark.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class ClassRequest {
    @NotBlank(message = "班级名称不能为空")
    private String name;

    @NotBlank(message = "年级不能为空")
    private String grade;

    private String description;

    private Long teacherId;

    private Integer maxStudents = 50;
}