package com.brainspark.repository;

import com.brainspark.entity.AssessmentTask;
import com.brainspark.entity.AssessmentTask.TaskStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface AssessmentTaskRepository extends JpaRepository<AssessmentTask, Long> {
    Page<AssessmentTask> findByClassId(Long classId, Pageable pageable);
    Page<AssessmentTask> findByTypeCode(String typeCode, Pageable pageable);
    Page<AssessmentTask> findByStatus(TaskStatus status, Pageable pageable);
    Page<AssessmentTask> findByTeacherId(Long teacherId, Pageable pageable);

    @Query("SELECT t FROM AssessmentTask t WHERE t.startAt <= ?1 AND t.endAt >= ?1")
    List<AssessmentTask> findActiveTasks(LocalDateTime now);

    @Query("SELECT t FROM AssessmentTask t WHERE t.classId = ?1 AND t.status = 'PENDING'")
    List<AssessmentTask> findPendingTasksByClassId(Long classId);

    long countByStatus(TaskStatus status);
}