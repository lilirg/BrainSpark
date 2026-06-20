package com.brainspark.controller;

import com.brainspark.dto.ReportResponse;
import com.brainspark.service.ReportService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/reports")
@RequiredArgsConstructor
public class ReportController {

    private final ReportService reportService;

    @GetMapping
    @PreAuthorize("hasAnyRole('PARENT', 'TEACHER', 'EMPLOYEE')")
    public ResponseEntity<List<ReportResponse>> getReports(
            @RequestParam Long studentId,
            @RequestParam(required = false) String type) {
        return ResponseEntity.ok(reportService.getReports(studentId, type));
    }

    @GetMapping("/{id}")
    @PreAuthorize("hasAnyRole('PARENT', 'TEACHER', 'EMPLOYEE')")
    public ResponseEntity<ReportResponse> getReport(@PathVariable Long id) {
        return ResponseEntity.ok(reportService.getReport(id));
    }

    @PostMapping("/{id}/share")
    @PreAuthorize("hasAnyRole('PARENT', 'TEACHER')")
    public ResponseEntity<Map<String, String>> shareReport(@PathVariable Long id) {
        String code = reportService.generateShareCode(id);
        return ResponseEntity.ok(Map.of("shareCode", code));
    }
}