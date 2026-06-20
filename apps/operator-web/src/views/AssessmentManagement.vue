<template>
  <div class="assessment-mgmt">
    <h2>测评管理</h2>
    <el-table :data="assessments" stripe style="width: 100%">
      <el-table-column prop="name" label="测评名称" />
      <el-table-column prop="type" label="类型" width="150" />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-switch
            :model-value="row.status === 'ACTIVE'"
            @change="(val: boolean) => toggleStatus(row.id, val)"
            active-text="启用"
            inactive-text="停用"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button type="primary" link>编辑</el-button>
          <el-button type="danger" link>删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '../apis/admin'
import { ElMessage } from 'element-plus'

const assessments = ref<any[]>([])

onMounted(async () => {
  try {
    const res = await adminApi.getAssessments()
    assessments.value = res.data
  } catch (e) {
    console.error('加载测评列表失败', e)
  }
})

async function toggleStatus(id: number, active: boolean) {
  try {
    await adminApi.updateAssessmentStatus(id, active ? 'ACTIVE' : 'INACTIVE')
    ElMessage.success('状态已更新')
  } catch (e) {
    ElMessage.error('更新失败')
  }
}
</script>