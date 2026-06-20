package com.brainspark.repository;

import com.brainspark.entity.AssessmentType;
import com.brainspark.entity.AssessmentType.Category;
import com.brainspark.entity.AssessmentType.Status;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AssessmentTypeRepository extends JpaRepository<AssessmentType, Long> {
    Optional<AssessmentType> findByCode(String code);
    boolean existsByCode(String code);
    Page<AssessmentType> findByCategory(Category category, Pageable pageable);
    Page<AssessmentType> findByStatus(Status status, Pageable pageable);
    List<AssessmentType> findByIsPublishedTrue();
    List<AssessmentType> findByMinAgeLessThanEqualAndMaxAgeGreaterThanEqual(int minAge, int maxAge);
}