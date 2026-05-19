<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>学生总数</span>
            </div>
          </template>
          <div class="count">{{ stats.totalStudents }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>已完成测评</span>
            </div>
          </template>
          <div class="count">{{ stats.completedAssessments }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>待处理报告</span>
            </div>
          </template>
          <div class="count">{{ stats.pendingReports }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>平均分</span>
            </div>
          </template>
          <div class="count">{{ stats.averageScore }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>能力维度分布</span>
          </template>
          <div ref="chartRef" style="width: 100%; height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近测评趋势</span>
          </template>
          <div ref="trendChartRef" style="width: 100%; height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const stats = ref({
  totalStudents: 156,
  completedAssessments: 89,
  pendingReports: 12,
  averageScore: 78.5,
})

const chartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()

onMounted(() => {
  if (chartRef.value) {
    const chart = echarts.init(chartRef.value)
    chart.setOption({
      radar: {
        indicator: [
          { name: '记忆力', max: 100 },
          { name: '注意力', max: 100 },
          { name: '逻辑力', max: 100 },
          { name: '创造力', max: 100 },
          { name: '观察力', max: 100 },
          { name: '想象力', max: 100 },
        ],
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: [85, 72, 68, 90, 78, 82],
              name: '平均能力',
            },
          ],
        },
      ],
    })
  }

  if (trendChartRef.value) {
    const chart = echarts.init(trendChartRef.value)
    chart.setOption({
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      },
      yAxis: { type: 'value' },
      series: [
        {
          data: [12, 15, 8, 20, 18, 5, 3],
          type: 'line',
          smooth: true,
        },
      ],
    })
  }
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.count {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  text-align: center;
}
</style>