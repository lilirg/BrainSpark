<template>
  <div class="report-detail">
    <el-button text @click="router.back()" class="mb-4">
      <el-icon><ArrowLeft /></el-icon> 返回
    </el-button>
    <el-card v-if="report">
      <template #header>
        <div class="report-header">
          <h2>{{ report.title }}</h2>
          <el-tag :type="report.status === 'COMPLETED' ? 'success' : 'warning'">
            {{ report.status === 'COMPLETED' ? '已完成' : '生成中' }}
          </el-tag>
        </div>
      </template>
      <p>学生: {{ report.studentName }}</p>
      <p>生成时间: {{ report.createdAt }}</p>
      <div class="mt-4" v-if="report.pdfUrl">
        <el-button type="primary" @click="downloadReport">下载 PDF</el-button>
      </div>
    </el-card>
    <el-empty v-else description="加载中..." />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { reportApi, type Report } from '../apis/report'
import { ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const report = ref<Report | null>(null)

onMounted(async () => {
  try {
    const res = await reportApi.getReport(Number(route.params.id))
    report.value = res.data
  } catch (e) {
    console.error('加载报告详情失败', e)
  }
})

function downloadReport() {
  if (report.value?.pdfUrl) {
    window.open(report.value.pdfUrl, '_blank')
  }
}
</script>

<style scoped>
.mb-4 { margin-bottom: 16px; }
.report-header { display: flex; justify-content: space-between; align-items: center; }
.mt-4 { margin-top: 16px; }
</style>