package com.brainspark.controller;

import com.brainspark.dto.*;
import com.brainspark.service.ParentService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/parent")
@RequiredArgsConstructor
@PreAuthorize("hasRole('PARENT')")
public class ParentController {

    private final ParentService parentService;

    @GetMapping("/children")
    public ResponseEntity<List<ChildResponse>> getChildren(@AuthenticationPrincipal Long userId) {
        return ResponseEntity.ok(parentService.getChildren(userId));
    }

    @GetMapping("/dashboard/{childId}")
    public ResponseEntity<ParentDashboardResponse> getDashboard(
            @AuthenticationPrincipal Long userId,
            @PathVariable Long childId) {
        return ResponseEntity.ok(parentService.getDashboard(userId, childId));
    }

    @GetMapping("/usage")
    public ResponseEntity<Map<String, Object>> getUsage(@AuthenticationPrincipal Long userId) {
        return ResponseEntity.ok(parentService.getUsageStats(userId));
    }

    @PutMapping("/settings")
    public ResponseEntity<Map<String, String>> updateSettings(
            @AuthenticationPrincipal Long userId,
            @RequestBody ParentSettingsRequest request) {
        parentService.updateSettings(userId, request);
        return ResponseEntity.ok(Map.of("message", "设置已更新"));
    }
}