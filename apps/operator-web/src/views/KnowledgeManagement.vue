<template>
  <div class="knowledge-mgmt">
    <h2>知识库管理</h2>
    <div class="toolbar">
      <el-button type="primary" @click="reindex">重建索引</el-button>
    </div>
    <el-table :data="docs" stripe style="width: 100%">
      <el-table-column prop="title" label="文档名称" />
      <el-table-column prop="status" label="索引状态" width="150">
        <template #default="{ row }">
          <el-tag :type="row.status === 'INDEXED' ? 'success' : 'warning'">
            {{ row.status === 'INDEXED' ? '已索引' : '待索引' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button type="primary" link>查看</el-button>
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

const docs = ref<any[]>([])

onMounted(async () => {
  try {
    const res = await adminApi.getKnowledgeDocs()
    docs.value = res.data
  } catch (e) {
    console.error('加载知识库失败', e)
  }
})

async function reindex() {
  try {
    await adminApi.reindexKnowledge()
    ElMessage.success('重建任务已提交')
  } catch (e) {
    ElMessage.error('重建失败')
  }
}
</script>

<style scoped>
.toolbar { margin-bottom: 16px; }
</style>