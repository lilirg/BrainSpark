package com.brainspark.controller;

import com.brainspark.dto.LoginRequest;
import com.brainspark.dto.LoginResponse;
import com.brainspark.dto.RefreshTokenRequest;
import com.brainspark.entity.User;
import com.brainspark.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    public ResponseEntity<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        return ResponseEntity.ok(authService.login(request));
    }

    @PostMapping("/refresh")
    public ResponseEntity<LoginResponse> refresh(@Valid @RequestBody RefreshTokenRequest request) {
        return ResponseEntity.ok(authService.refresh(request));
    }

    @PostMapping("/logout")
    public ResponseEntity<Map<String, String>> logout(
            @RequestHeader("Authorization") String authHeader) {
        String token = authHeader.replace("Bearer ", "");
        authService.logout(token);
        return ResponseEntity.ok(Map.of("message", "登出成功"));
    }

    @GetMapping("/me")
    public ResponseEntity<User> me(@AuthenticationPrincipal Long userId) {
        return ResponseEntity.ok(authService.getCurrentUser(userId));
    }
}