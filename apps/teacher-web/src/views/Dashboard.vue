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

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近测评活动</span>
              <el-button size="small" type="primary" @click="refreshData">刷新</el-button>
            </div>
          </template>
          <el-table :data="recentActivities" stripe>
            <el-table-column prop="studentName" label="学生姓名" width="120" />
            <el-table-column prop="assessmentName" label="测评名称" width="150" />
            <el-table-column prop="className" label="班级" width="120" />
            <el-table-column prop="score" label="得分" width="80">
              <template #default="{ row }">
                <el-tag :type="row.score >= 80 ? 'success' : row.score >= 60 ? '' : 'warning'">
                  {{ row.score }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="date" label="测评时间" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { assessmentApi } from '../apis/assessment'
import { classApi } from '../apis/class'
import { ElMessage } from 'element-plus'

interface RecentActivity {
  studentName: string
  assessmentName: string
  className: string
  score: number
  date: string
}

const stats = ref({
  totalStudents: 0,
  completedAssessments: 0,
  pendingReports: 0,
  averageScore: 0,
})

const recentActivities = ref<RecentActivity[]>([])

const chartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
let radarChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

async function loadDashboardData() {
  try {
    const [tasksRes, classesRes] = await Promise.all([
      assessmentApi.getTodayTasks(),
      classApi.getClasses()
    ])
    
    const tasks = tasksRes.data ?? { inProgress: 0, completed: 0 }
    const classList = classesRes.content ?? []
    
    stats.value = {
      totalStudents: classList.reduce((sum, c) => sum + (c.maxStudents ?? 0), 0),
      completedAssessments: tasks.completed ?? 0,
      pendingReports: tasks.inProgress ?? 0,
      averageScore: 78.5
    }

    recentActivities.value = [
      { studentName: '张明', assessmentName: '舒尔特方格', className: '一年级三班', score: 85, date: '2025-05-15 14:30' },
      { studentName: '李华', assessmentName: '数字广度', className: '二年级一班', score: 72, date: '2025-05-15 14:15' },
      { studentName: '王芳', assessmentName: '舒尔特方格', className: '一年级三班', score: 90, date: '2025-05-15 13:50' },
      { studentName: '赵强', assessmentName: '模式识别', className: '三年级五班', score: 68, date: '2025-05-14 16:00' },
    ]
  } catch (e) {
    console.error('加载仪表板数据失败', e)
    ElMessage.error('加载数据失败')
  }
}

function initCharts() {
  if (chartRef.value) {
    radarChart = echarts.init(chartRef.value)
    radarChart.setOption({
      radar: {
        indicator: [
          { name: '记忆力', max: 100 },
          { name: '注意力', max: 100 },
          { name: '逻辑力', max: 100 },
          { name: '创造力', max: 100 },
          { name: '观察力', max: 100 },
          { name: '想象力', max: 100 },
        ],
        radius: '65%'
      },
      legend: {
        data: ['平均能力', '班级最高'],
        bottom: 10
      },
      series: [
        {
          name: '平均能力',
          type: 'radar',
          data: [
            {
              value: [85, 72, 68, 90, 78, 82],
              name: '平均能力',
              areaStyle: { opacity: 0.1 }
            }
          ]
        },
        {
          name: '班级最高',
          type: 'radar',
          data: [
            {
              value: [95, 88, 85, 96, 92, 90],
              name: '班级最高',
              areaStyle: { opacity: 0.05 }
            }
          ]
        }
      ]
    })
  }

  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: { type: 'value', name: '测评次数' },
      series: [
        {
          name: '测评次数',
          type: 'line',
          smooth: true,
          data: [12, 15, 8, 20, 18, 5, 3],
          areaStyle: { opacity: 0.1 },
          itemStyle: { color: '#409eff' }
        }
      ]
    })
  }
}

function refreshData() {
  loadDashboardData()
  ElMessage.success('数据已刷新')
}

onMounted(() => {
  loadDashboardData()
  initCharts()
})

onBeforeUnmount(() => {
  radarChart?.dispose()
  trendChart?.dispose()
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