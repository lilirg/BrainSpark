<template>
  <div class="growth-tracking">
    <h2>成长追踪</h2>
    <el-card>
      <template #header>
        <div class="growth-header">
          <span>认知维度变化趋势</span>
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" size="small" />
        </div>
      </template>
      <div ref="chartRef" style="height: 400px"></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const chartRef = ref<HTMLDivElement>()
const dateRange = ref<[Date, Date]>([new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), new Date()])

onMounted(() => {
  if (chartRef.value) {
    const chart = echarts.init(chartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['注意力', '记忆力', '逻辑推理'] },
      xAxis: { type: 'category', data: ['第1周', '第2周', '第3周', '第4周'] },
      yAxis: { type: 'value', min: 0, max: 100 },
      series: [
        { name: '注意力', type: 'line', data: [65, 72, 78, 85] },
        { name: '记忆力', type: 'line', data: [60, 65, 70, 72] },
        { name: '逻辑推理', type: 'line', data: [55, 60, 68, 75] }
      ]
    })
  }
})
</script>

<style scoped>
.growth-header { display: flex; justify-content: space-between; align-items: center; }
</style>