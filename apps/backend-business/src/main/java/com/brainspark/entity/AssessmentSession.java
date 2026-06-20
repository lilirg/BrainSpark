package com.brainspark.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "assessment_sessions", schema = "assessment_schema")
@AllArgsConstructor
@NoArgsConstructor
public class AssessmentSession {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "session_id", nullable = false, unique = true, length = 36)
    private String sessionId;

    @Column(name = "task_code", nullable = false, length = 32)
    private String taskCode;

    @Column(name = "student_id", nullable = false)
    private Long studentId;

    @Column(name = "type_id", nullable = false)
    private Long typeId;

    @Column(name = "start_time", nullable = false)
    private LocalDateTime startTime;

    @Column(name = "end_time")
    private LocalDateTime endTime;

    @Column(name = "total_time_sec")
    private Float totalTimeSec;

    @Column(name = "grid_size")
    private Integer gridSize;

    @Column(name = "is_completed")
    private Integer isCompleted = 0;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private SessionStatus status = SessionStatus.PENDING;

    @Column(name = "device_info", columnDefinition = "JSON")
    private String deviceInfo;

    @Column(updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    public enum SessionStatus {
        PENDING, IN_PROGRESS, PAUSED, COMPLETED, ABANDONED
    }

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}