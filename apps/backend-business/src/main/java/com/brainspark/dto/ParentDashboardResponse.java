package com.brainspark.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ParentDashboardResponse {
    private ChildResponse child;
    private Integer pendingReports;
    private Integer completedAssessments;
    private Double averageScore;
    private List<Map<String, Object>> recentActivities;
    private List<CognitiveDimensionDTO> cognitiveProfile;
}