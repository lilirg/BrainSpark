<template>
  <div class="assessment-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>测评管理</span>
          <el-button type="primary">发起新测评</el-button>
        </div>
      </template>

      <el-table :data="assessments" style="width: 100%">
        <el-table-column prop="name" label="测评名称" />
        <el-table-column prop="type" label="类型" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="studentCount" label="参与人数" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetails(row.id)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Assessment {
  id: number
  name: string
  type: string
  status: 'draft' | 'active' | 'completed'
  studentCount: number
}

const assessments = ref<Assessment[]>([
  { id: 1, name: '注意力集中测试', type: '认知测评', status: 'active', studentCount: 28 },
  { id: 2, name: '记忆力评估', type: '认知测评', status: 'completed', studentCount: 30 },
  { id: 3, name: '注意力集中测试', type: '认知测评', status: 'draft', studentCount: 0 },
])

const getStatusType = (status: string) => {
  const map = { draft: 'info', active: 'success', completed: 'warning' }
  return map[status as keyof typeof map] || 'info'
}

const getStatusText = (status: string) => {
  const map = { draft: '草稿', active: '进行中', completed: '已完成' }
  return map[status as keyof typeof map] || '未知'
}

const viewDetails = (id: number) => {
  console.log('查看详情:', id)
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>