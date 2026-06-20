<template>
  <div class="dashboard">
    <h2>仪表板</h2>
    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20" class="mt-4">
      <el-col :span="12">
        <el-card>
          <template #header>认知维度概览</template>
          <div v-if="dashboard?.cognitiveProfile?.length">
            <div v-for="dim in dashboard.cognitiveProfile" :key="dim.name" class="dimension-item">
              <div class="dimension-header">
                <span>{{ dim.name }}</span>
                <span :class="'level-' + dim.level.toLowerCase()">{{ dim.level }}</span>
              </div>
              <el-progress :percentage="dim.score" :color="dim.score >= 80 ? '#67c23a' : dim.score >= 60 ? '#e6a23c' : '#f56c6c'" />
            </div>
          </div>
          <el-empty v-else description="暂无数据" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>最近活动</template>
          <el-timeline v-if="dashboard?.recentActivities?.length">
            <el-timeline-item v-for="act in dashboard.recentActivities" :key="act.time" :timestamp="act.time">
              {{ act.content }}
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无活动" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { parentApi, type ParentDashboard } from '../apis/parent'

const dashboard = ref<ParentDashboard | null>(null)
const stats = ref([
  { label: '待处理报告', value: 0 },
  { label: '已完成测评', value: 0 },
  { label: '平均得分', value: 0 },
  { label: '本周活跃', value: 0 }
])

onMounted(async () => {
  try {
    const childrenRes = await parentApi.getChildren()
    if (childrenRes.data?.length) {
      const res = await parentApi.getDashboard(childrenRes.data[0].id)
      dashboard.value = res.data
      stats.value = [
        { label: '待处理报告', value: res.data.pendingReports },
        { label: '已完成测评', value: res.data.completedAssessments },
        { label: '平均得分', value: res.data.averageScore },
        { label: '本周活跃', value: 5 }
      ]
    }
  } catch (e) {
    console.error('加载仪表板失败', e)
  }
})
</script>

<style scoped>
.stat-card { text-align: center; }
.stat-value { font-size: 32px; font-weight: 700; color: #409eff; }
.stat-label { font-size: 14px; color: #909399; margin-top: 8px; }
.mt-4 { margin-top: 16px; }
.dimension-item { margin-bottom: 16px; }
.dimension-header { display: flex; justify-content: space-between; margin-bottom: 4px; }
.level-high { color: #67c23a; }
.level-average { color: #e6a23c; }
.level-low { color: #f56c6c; }
</style>