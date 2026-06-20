package com.brainspark.repository;

import com.brainspark.entity.AssessmentSession;
import com.brainspark.entity.AssessmentSession.SessionStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AssessmentSessionRepository extends JpaRepository<AssessmentSession, Long> {
    Optional<AssessmentSession> findBySessionId(String sessionId);
    Page<AssessmentSession> findByStudentId(Long studentId, Pageable pageable);
    Page<AssessmentSession> findByTypeId(Long typeId, Pageable pageable);
    Page<AssessmentSession> findByStatus(SessionStatus status, Pageable pageable);
    List<AssessmentSession> findByStudentIdAndStatus(Long studentId, SessionStatus status);
    long countByStudentIdAndStatus(Long studentId, SessionStatus status);
}