<template>
  <div class="student-profile">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <div class="student-info">
            <el-avatar :size="100" src="">张明</el-avatar>
            <h3>{{ student.name }}</h3>
            <p>班级：{{ student.className }}</p>
            <p>学号：{{ student.studentId }}</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="18">
        <el-card>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="认知能力雷达图" name="radar">
              <div ref="radarChartRef" style="height: 300px"></div>
            </el-tab-pane>
            <el-tab-pane label="历史记录" name="history">
              <el-timeline>
                <el-timeline-item
                  v-for="record in student.history"
                  :key="record.id"
                  :timestamp="record.date"
                  placement="top"
                >
                  <el-card>
                    <h4>{{ record.name }}</h4>
                    <p>综合评分：{{ record.score }}</p>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </el-tab-pane>
            <el-tab-pane label="AI 建议" name="suggestions">
              <div v-loading="suggestionsLoading">
                <p>{{ student.aiSuggestions }}</p>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

interface StudentHistory {
  id: number
  name: string
  date: string
  score: number
}

interface Student {
  name: string
  className: string
  studentId: string
  history: StudentHistory[]
  aiSuggestions: string
}

const activeTab = ref('radar')
const radarChartRef = ref<HTMLElement>()
const suggestionsLoading = ref(false)

const student = ref<Student>({
  name: '张明',
  className: '一年级三班',
  studentId: '20250001',
  history: [
    { id: 1, name: '注意力测试', date: '2025-05-15', score: 82 },
    { id: 2, name: '记忆力评估', date: '2025-04-20', score: 75 },
    { id: 3, name: '认知能力综合测评', date: '2025-03-10', score: 78 },
  ],
  aiSuggestions: '根据该生的评估结果，建议在注意力训练方面加强专注度练习，同时通过记忆游戏提升记忆力表现。',
})

onMounted(() => {
  if (radarChartRef.value) {
    const chart = echarts.init(radarChartRef.value)
    chart.setOption({
      radar: {
        indicator: [
          { name: '记忆力', max: 100 },
          { name: '注意力', max: 100 },
          { name: '逻辑力', max: 100 },
          { name: '创造力', max: 100 },
          { name: '观察力', max: 100 },
        ],
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: [75, 82, 68, 85, 78],
              name: '张明',
            },
          ],
        },
      ],
    })
  }
})
</script>

<style scoped>
.student-profile {
  padding: 20px;
}

.student-info {
  text-align: center;
  padding: 20px 0;
}

.student-info h3 {
  margin: 10px 0 5px;
  color: #303133;
}

.student-info p {
  margin: 5px 0;
  color: #606266;
}
</style>