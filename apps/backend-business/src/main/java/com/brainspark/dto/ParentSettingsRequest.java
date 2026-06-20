package com.brainspark.dto;

import lombok.Data;

@Data
public class ParentSettingsRequest {
    private Boolean dailyReport;
    private Boolean weeklyReport;
    private Boolean assessmentReminder;
    private Boolean growthAlert;
    private Integer dailyTimeLimit;
    private String nightTimeStart;
    private String nightTimeEnd;
}