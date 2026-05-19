<template>
  <div class="report-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报告查看</span>
          <el-input
            v-model="searchText"
            placeholder="搜索学生姓名"
            style="width: 200px"
            clearable
          />
        </div>
      </template>

      <el-table :data="filteredReports" style="width: 100%">
        <el-table-column prop="studentName" label="学生姓名" />
        <el-table-column prop="class" label="班级" />
        <el-table-column prop="date" label="测评日期" />
        <el-table-column prop="type" label="报告类型" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="viewReport(row.id)">
              查看报告
            </el-button>
            <el-button size="small" type="success" @click="shareReport(row.id)">
              分享
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="AI 报告详情" width="600px">
      <div class="report-content" v-loading="loading">
        <h3>认知能力评估报告</h3>
        <p><strong>学生:</strong> {{ reportData.studentName }}</p>
        <p><strong>评估日期:</strong> {{ reportData.date }}</p>
        <p><strong>综合评分:</strong> {{ reportData.overallScore }}</p>
        <el-divider />
        <h4>评估概要</h4>
        <p>{{ reportData.summary }}</p>
        <h4>建议</h4>
        <p>{{ reportData.suggestions }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Report {
  id: number
  studentName: string
  class: string
  date: string
  type: string
}

const reports = ref<Report[]>([
  { id: 1, studentName: '小明', class: '一年级三班', date: '2025-05-15', type: '认知评估' },
  { id: 2, studentName: '小红', class: '二年级一班', date: '2025-05-14', type: '注意力评估' },
  { id: 3, studentName: '小刚', class: '三年级五班', date: '2025-05-13', type: '记忆力评估' },
])

const searchText = ref('')
const dialogVisible = ref(false)
const loading = ref(false)

const filteredReports = computed(() => {
  if (!searchText.value) return reports.value
  return reports.value.filter((r) =>
    r.studentName.includes(searchText.value)
  )
})

const reportData = ref({
  studentName: '',
  date: '',
  overallScore: 0,
  summary: '',
  suggestions: '',
})

const viewReport = (id: number) => {
  loading.value = true
  // 模拟 API 调用
  setTimeout(() => {
    reportData.value = {
      studentName: '小明',
      date: '2025-05-15',
      overallScore: 85,
      summary:
        '该学生在注意力和创造力维度表现突出，记忆力维度略低于同龄人平均水平，建议进行针对性训练。',
      suggestions:
        '1. 建议每日进行注意力训练课程\n2. 增加记忆力游戏练习\n3. 保持创造力培养',
    }
    dialogVisible.value = true
    loading.value = false
  }, 500)
}

const shareReport = (id: number) => {
  console.log('分享报告:', id)
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-content {
  padding: 10px;
}

.report-content h3 {
  margin-top: 0;
  color: #409eff;
}

.report-content h4 {
  margin-top: 16px;
  color: #303133;
}

.report-content p {
  line-height: 1.8;
  color: #606266;
}
</style>