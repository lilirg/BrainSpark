<template>
  <div class="dashboard">
    <h2>工作台</h2>
    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
          <div class="stat-change" :class="stat.change > 0 ? 'up' : 'down'">
            {{ stat.change > 0 ? '+' : '' }}{{ stat.change }}%
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20" class="mt-4">
      <el-col :span="16">
        <el-card>
          <template #header>用户增长趋势</template>
          <div ref="chartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>快速操作</template>
          <div class="quick-actions">
            <el-button type="primary" class="action-btn" @click="$router.push('/notifications')">
              发送通知
            </el-button>
            <el-button type="success" class="action-btn" @click="$router.push('/assessments')">
              管理测评
            </el-button>
            <el-button type="warning" class="action-btn" @click="$router.push('/knowledge')">
              知识库管理
            </el-button>
            <el-button type="info" class="action-btn" @click="$router.push('/partners')">
              机构合作
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const chartRef = ref<HTMLDivElement>()
const stats = ref([
  { label: '总用户数', value: '12,580', change: 15.8 },
  { label: '活跃用户', value: '3,842', change: 8.2 },
  { label: '今日新增', value: '89', change: 12.5 },
  { label: '完成率', value: '87.5%', change: 3.2 }
])

onMounted(() => {
  if (chartRef.value) {
    const chart = echarts.init(chartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
      yAxis: { type: 'value' },
      series: [
        { name: '新增用户', type: 'bar', data: [820, 932, 901, 1234, 1290, 1330] },
        { name: '活跃用户', type: 'line', data: [620, 732, 801, 934, 1090, 1130] }
      ]
    })
  }
})
</script>

<style scoped>
.stat-card { text-align: center; }
.stat-value { font-size: 28px; font-weight: 700; color: #409eff; }
.stat-label { font-size: 14px; color: #909399; margin-top: 4px; }
.stat-change { font-size: 12px; margin-top: 4px; }
.stat-change.up { color: #67c23a; }
.stat-change.down { color: #f56c6c; }
.mt-4 { margin-top: 16px; }
.quick-actions { display: flex; flex-direction: column; gap: 12px; }
.action-btn { width: 100%; }
</style>