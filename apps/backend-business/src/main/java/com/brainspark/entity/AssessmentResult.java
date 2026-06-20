package com.brainspark.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "assessment_results", schema = "assessment_schema")
@AllArgsConstructor
@NoArgsConstructor
public class AssessmentResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "task_id")
    private Long taskId;

    @Column(name = "type_code", nullable = false, length = 50)
    private String typeCode;

    @Column(name = "request_id", length = 100)
    private String requestId;

    @Column(name = "session_id", length = 100)
    private String sessionId;

    @Column(name = "score_data", columnDefinition = "JSON")
    private String scoreData;

    @Column(name = "cognitive_profile", columnDefinition = "JSON")
    private String cognitiveProfile;

    @Column(name = "ai_recommendations", columnDefinition = "JSON")
    private String aiRecommendations;

    @Enumerated(EnumType.STRING)
    @Column(name = "report_status", nullable = false, length = 20)
    private ReportStatus reportStatus = ReportStatus.PENDING;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private ResultStatus status = ResultStatus.FINISHED;

    @Column(name = "started_at")
    private LocalDateTime startedAt;

    @Column(name = "completed_at")
    private LocalDateTime completedAt;

    @Column(updatable = false)
    private LocalDateTime createdAt;

    public enum ReportStatus {
        PENDING, PROCESSING, COMPLETED, FAILED
    }

    public enum ResultStatus {
        FINISHED, PROCESSING, FAILED
    }

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}