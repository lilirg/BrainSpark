<template>
  <div class="report-list">
    <h2>报告中心</h2>
    <el-table :data="reports" stripe style="width: 100%">
      <el-table-column prop="title" label="报告名称" />
      <el-table-column prop="type" label="类型" width="120">
        <template #default="{ row }">
          <el-tag :type="row.type === 'ASSESSMENT' ? 'primary' : 'success'">
            {{ row.type === 'ASSESSMENT' ? '测评报告' : '成长报告' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'COMPLETED' ? 'success' : 'warning'">
            {{ row.status === 'COMPLETED' ? '已完成' : '生成中' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createdAt" label="生成时间" width="180" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button type="primary" link @click="viewReport(row.id)">查看</el-button>
          <el-button type="success" link @click="shareReport(row.id)">分享</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { reportApi, type Report } from '../apis/report'
import { ElMessage } from 'element-plus'

const router = useRouter()
const reports = ref<Report[]>([])

onMounted(async () => {
  try {
    const res = await reportApi.getReports(1)
    reports.value = res.data
  } catch (e) {
    console.error('加载报告列表失败', e)
  }
})

function viewReport(id: number) {
  router.push(`/reports/${id}`)
}

async function shareReport(id: number) {
  try {
    const res = await reportApi.shareReport(id)
    ElMessage.success(`分享码: ${res.data.shareCode}`)
  } catch (e) {
    ElMessage.error('分享失败')
  }
}
</script>