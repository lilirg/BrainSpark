package com.brainspark.service;

import com.brainspark.dto.ReportResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ReportService {

    public List<ReportResponse> getReports(Long studentId, String type) {
        // TODO: 从 reports 表查询
        return List.of(
            ReportResponse.builder()
                .id(1L).studentId(studentId).studentName("小明")
                .type("ASSESSMENT").title("注意力测评报告")
                .status("COMPLETED")
                .createdAt(LocalDateTime.now().minusDays(1))
                .build()
        );
    }

    public ReportResponse getReport(Long id) {
        return ReportResponse.builder()
            .id(id).studentId(1L).studentName("小明")
            .type("ASSESSMENT").title("注意力测评报告")
            .status("COMPLETED").pdfUrl("/reports/1.pdf")
            .shareCode(UUID.randomUUID().toString().substring(0, 8))
            .createdAt(LocalDateTime.now().minusDays(1))
            .build();
    }

    public String generateShareCode(Long id) {
        return UUID.randomUUID().toString().substring(0, 8);
    }
}