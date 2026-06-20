package com.brainspark.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportResponse {
    private Long id;
    private Long studentId;
    private String studentName;
    private String type;
    private String title;
    private String status;
    private String pdfUrl;
    private String shareCode;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}