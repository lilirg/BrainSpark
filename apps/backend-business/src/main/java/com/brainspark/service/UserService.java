package com.brainspark.service;

import com.brainspark.dto.*;
import com.brainspark.entity.User;
import com.brainspark.entity.User.Role;
import com.brainspark.entity.User.UserStatus;
import com.brainspark.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public Page<UserResponse> getUsers(String role, String status, Pageable pageable) {
        Page<User> users;
        if (role != null && status != null) {
            users = userRepository.findByRoleAndStatus(Role.valueOf(role), UserStatus.valueOf(status), pageable);
        } else if (role != null) {
            users = userRepository.findByRole(Role.valueOf(role), pageable);
        } else if (status != null) {
            users = userRepository.findByStatus(UserStatus.valueOf(status), pageable);
        } else {
            users = userRepository.findAll(pageable);
        }
        return users.map(this::toUserResponse);
    }

    public UserResponse getUser(Long id) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        return toUserResponse(user);
    }

    @Transactional
    public UserResponse createUser(UserCreateRequest request) {
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new RuntimeException("用户名已存在");
        }
        if (request.getEmail() != null && userRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException("邮箱已被使用");
        }

        User user = new User();
        user.setUsername(request.getUsername());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setEmail(request.getEmail());
        user.setRealName(request.getRealName());
        user.setAvatar(request.getAvatar());
        user.setRole(request.getRole());
        user.setStatus(UserStatus.ACTIVE);

        user = userRepository.save(user);
        return toUserResponse(user);
    }

    @Transactional
    public UserResponse updateUser(Long id, UserUpdateRequest request) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("用户不存在"));

        if (request.getEmail() != null) {
            user.setEmail(request.getEmail());
        }
        if (request.getRealName() != null) {
            user.setRealName(request.getRealName());
        }
        if (request.getAvatar() != null) {
            user.setAvatar(request.getAvatar());
        }
        if (request.getStatus() != null) {
            user.setStatus(UserStatus.valueOf(request.getStatus()));
        }

        user = userRepository.save(user);
        return toUserResponse(user);
    }

    @Transactional
    public void deleteUser(Long id) {
        if (!userRepository.existsById(id)) {
            throw new RuntimeException("用户不存在");
        }
        userRepository.deleteById(id);
    }

    @Transactional
    public void resetPassword(Long id, ResetPasswordRequest request) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        user.setPassword(passwordEncoder.encode(request.getNewPassword()));
        userRepository.save(user);
    }

    @Transactional
    public void bindParent(Long studentId, BindParentRequest request) {
        // 验证学生存在
        User student = userRepository.findById(studentId)
                .orElseThrow(() -> new RuntimeException("学生不存在"));
        if (student.getRole() != Role.STUDENT) {
            throw new RuntimeException("只能为学生绑定家长");
        }

        // 验证家长存在
        User parent = userRepository.findById(request.getParentId())
                .orElseThrow(() -> new RuntimeException("家长不存在"));
        if (parent.getRole() != Role.PARENT) {
            throw new RuntimeException("绑定的用户不是家长角色");
        }

        // 这里可以添加 family_bindings 表的操作
        // 由于 family_bindings 表在 MySQL 中，后续通过 JPA 实体操作
    }

    private UserResponse toUserResponse(User user) {
        return UserResponse.builder()
                .id(user.getId())
                .username(user.getUsername())
                .email(user.getEmail())
                .realName(user.getRealName())
                .avatar(user.getAvatar())
                .role(user.getRole())
                .status(user.getStatus())
                .lastLoginAt(user.getLastLoginAt())
                .createdAt(user.getCreatedAt())
                .updatedAt(user.getUpdatedAt())
                .build();
    }
}