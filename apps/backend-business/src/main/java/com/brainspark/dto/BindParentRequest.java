package com.brainspark.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class BindParentRequest {
    @NotBlank(message = "家长ID不能为空")
    private Long parentId;

    private String relationship;
}