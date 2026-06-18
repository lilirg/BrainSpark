package com.brainspark.service;

import com.brainspark.dto.LoginRequest;
import com.brainspark.dto.LoginResponse;
import com.brainspark.dto.RefreshTokenRequest;
import com.brainspark.entity.User;
import com.brainspark.repository.UserRepository;
import com.brainspark.utils.JwtUtil;
import io.jsonwebtoken.Claims;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.concurrent.TimeUnit;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;
    private final StringRedisTemplate redisTemplate;

    @Value("${jwt.access-expiration}")
    private long accessExpiration;

    @Value("${jwt.refresh-expiration}")
    private long refreshExpiration;

    public LoginResponse login(LoginRequest request) {
        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> new BadCredentialsException("用户名或密码错误"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new BadCredentialsException("用户名或密码错误");
        }

        if (user.getStatus() != User.UserStatus.ACTIVE) {
            throw new BadCredentialsException("账户已被锁定或禁用");
        }

        String accessToken = jwtUtil.generateAccessToken(user.getId(), user.getUsername(), user.getRole().name());
        String refreshToken = jwtUtil.generateRefreshToken(user.getId());

        // 存储到 Redis 白名单
        redisTemplate.opsForValue().set(
                "jwt:whitelist:" + accessToken,
                user.getId().toString(),
                accessExpiration,
                TimeUnit.SECONDS
        );

        // 更新最后登录时间
        user.setLastLoginAt(LocalDateTime.now());
        userRepository.save(user);

        return new LoginResponse(accessToken, refreshToken, "Bearer", accessExpiration);
    }

    public LoginResponse refresh(RefreshTokenRequest request) {
        if (!jwtUtil.validateToken(request.getRefreshToken())) {
            throw new BadCredentialsException("刷新令牌无效或已过期");
        }

        Claims claims = jwtUtil.parseToken(request.getRefreshToken());
        if (!"refresh".equals(claims.get("type"))) {
            throw new BadCredentialsException("无效的刷新令牌");
        }

        Long userId = Long.parseLong(claims.getSubject());
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BadCredentialsException("用户不存在"));

        String newAccessToken = jwtUtil.generateAccessToken(user.getId(), user.getUsername(), user.getRole().name());
        String newRefreshToken = jwtUtil.generateRefreshToken(user.getId());

        // 存储新 Token 到 Redis
        redisTemplate.opsForValue().set(
                "jwt:whitelist:" + newAccessToken,
                user.getId().toString(),
                accessExpiration,
                TimeUnit.SECONDS
        );

        return new LoginResponse(newAccessToken, newRefreshToken, "Bearer", accessExpiration);
    }

    public void logout(String token) {
        // 将 Token 加入黑名单
        redisTemplate.opsForValue().set(
                "jwt:blacklist:" + token,
                "true",
                accessExpiration,
                TimeUnit.SECONDS
        );
        // 从白名单移除
        redisTemplate.delete("jwt:whitelist:" + token);
    }

    public User getCurrentUser(Long userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
    }
}