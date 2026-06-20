package com.brainspark.service;

import com.brainspark.dto.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

@Service
@RequiredArgsConstructor
public class ParentService {

    public List<ChildResponse> getChildren(Long parentId) {
        // TODO: 从 family_bindings 表查询关联的学生
        // 当前返回模拟数据
        return List.of(
            ChildResponse.builder()
                .id(1L).name("小明").studentCode("STU001")
                .gender("MALE").age(8).grade("二年级")
                .className("二年级一班").totalAssessments(12)
                .status("ACTIVE").build()
        );
    }

    public ParentDashboardResponse getDashboard(Long parentId, Long childId) {
        // TODO: 从 assessment_results 表聚合数据
        return ParentDashboardResponse.builder()
            .child(getChildren(parentId).get(0))
            .pendingReports(2)
            .completedAssessments(12)
            .averageScore(78.5)
            .recentActivities(new ArrayList<>())
            .cognitiveProfile(List.of(
                CognitiveDimensionDTO.builder()
                    .name("注意力").score(85.0).percentile(72.0)
                    .level("HIGH").description("注意力集中能力优秀")
                    .suggestion("继续保持").build(),
                CognitiveDimensionDTO.builder()
                    .name("记忆力").score(70.0).percentile(55.0)
                    .level("AVERAGE").description("工作记忆容量正常")
                    .suggestion("可通过数字广度游戏提升").build()
            )).build();
    }

    public Map<String, Object> getUsageStats(Long parentId) {
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalTime", 3600); // 分钟
        stats.put("dailyAverage", 25);
        stats.put("weeklyActive", 5);
        stats.put("lastActive", "2026-06-18T10:30:00");
        return stats;
    }

    @Transactional
    public void updateSettings(Long parentId, ParentSettingsRequest request) {
        // TODO: 保存家长设置到数据库
    }
}