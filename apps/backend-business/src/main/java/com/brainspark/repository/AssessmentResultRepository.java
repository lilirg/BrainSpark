package com.brainspark.repository;

import com.brainspark.entity.AssessmentResult;
import com.brainspark.entity.AssessmentResult.ReportStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AssessmentResultRepository extends JpaRepository<AssessmentResult, Long> {
    Page<AssessmentResult> findByUserId(Long userId, Pageable pageable);
    Page<AssessmentResult> findByTypeCode(String typeCode, Pageable pageable);
    Page<AssessmentResult> findByReportStatus(ReportStatus reportStatus, Pageable pageable);
    Optional<AssessmentResult> findBySessionId(String sessionId);
    List<AssessmentResult> findByUserIdAndTypeCode(Long userId, String typeCode);
    long countByUserId(Long userId);
}