package com.brainspark.repository;

import com.brainspark.entity.SchoolClass;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface SchoolClassRepository extends JpaRepository<SchoolClass, Long> {
    Page<SchoolClass> findByTeacherId(Long teacherId, Pageable pageable);
    Page<SchoolClass> findByGrade(String grade, Pageable pageable);
    Page<SchoolClass> findByIsActive(Boolean isActive, Pageable pageable);
    List<SchoolClass> findByTeacherIdAndIsActive(Long teacherId, Boolean isActive);
    long countByTeacherId(Long teacherId);
}