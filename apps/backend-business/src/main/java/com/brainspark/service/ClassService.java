package com.brainspark.service;

import com.brainspark.dto.ClassRequest;
import com.brainspark.dto.ClassResponse;
import com.brainspark.entity.SchoolClass;
import com.brainspark.repository.SchoolClassRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class ClassService {

    private final SchoolClassRepository schoolClassRepository;

    public Page<ClassResponse> getClasses(Long teacherId, String grade, Pageable pageable) {
        Page<SchoolClass> classes;
        if (teacherId != null) {
            classes = schoolClassRepository.findByTeacherId(teacherId, pageable);
        } else if (grade != null) {
            classes = schoolClassRepository.findByGrade(grade, pageable);
        } else {
            classes = schoolClassRepository.findAll(pageable);
        }
        return classes.map(this::toClassResponse);
    }

    public ClassResponse getClass(Long id) {
        SchoolClass schoolClass = schoolClassRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("班级不存在"));
        return toClassResponse(schoolClass);
    }

    @Transactional
    public ClassResponse createClass(ClassRequest request) {
        SchoolClass schoolClass = new SchoolClass();
        schoolClass.setName(request.getName());
        schoolClass.setGrade(request.getGrade());
        schoolClass.setDescription(request.getDescription());
        schoolClass.setTeacherId(request.getTeacherId());
        schoolClass.setMaxStudents(request.getMaxStudents());
        schoolClass.setIsActive(true);

        schoolClass = schoolClassRepository.save(schoolClass);
        return toClassResponse(schoolClass);
    }

    @Transactional
    public ClassResponse updateClass(Long id, ClassRequest request) {
        SchoolClass schoolClass = schoolClassRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("班级不存在"));

        if (request.getName() != null) schoolClass.setName(request.getName());
        if (request.getGrade() != null) schoolClass.setGrade(request.getGrade());
        if (request.getDescription() != null) schoolClass.setDescription(request.getDescription());
        if (request.getTeacherId() != null) schoolClass.setTeacherId(request.getTeacherId());
        if (request.getMaxStudents() != null) schoolClass.setMaxStudents(request.getMaxStudents());

        schoolClass = schoolClassRepository.save(schoolClass);
        return toClassResponse(schoolClass);
    }

    @Transactional
    public void deleteClass(Long id) {
        if (!schoolClassRepository.existsById(id)) {
            throw new RuntimeException("班级不存在");
        }
        schoolClassRepository.deleteById(id);
    }

    private ClassResponse toClassResponse(SchoolClass schoolClass) {
        return ClassResponse.builder()
                .id(schoolClass.getId())
                .orgId(schoolClass.getOrgId())
                .name(schoolClass.getName())
                .grade(schoolClass.getGrade())
                .description(schoolClass.getDescription())
                .teacherId(schoolClass.getTeacherId())
                .maxStudents(schoolClass.getMaxStudents())
                .isActive(schoolClass.getIsActive())
                .createdAt(schoolClass.getCreatedAt())
                .updatedAt(schoolClass.getUpdatedAt())
                .build();
    }
}