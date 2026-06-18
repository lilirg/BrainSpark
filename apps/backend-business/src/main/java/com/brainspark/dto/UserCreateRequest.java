package com.brainspark.dto;

import com.brainspark.entity.User.Role;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class UserCreateRequest {
    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 50, message = "用户名长度3-50个字符")
    private String username;

    @NotBlank(message = "密码不能为空")
    @Size(min = 6, max = 100, message = "密码长度6-100个字符")
    private String password;

    @Email(message = "邮箱格式不正确")
    private String email;

    private String realName;

    private String avatar;

    @NotBlank(message = "角色不能为空")
    private Role role;
}