package com.brainspark.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class ResetPasswordRequest {
    @NotBlank(message = "新密码不能为空")
    @Size(min = 6, max = 100, message = "密码长度6-100个字符")
    private String newPassword;
}