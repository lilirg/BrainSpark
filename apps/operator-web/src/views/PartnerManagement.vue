<template>
  <div class="partner-mgmt">
    <h2>机构合作管理</h2>
    <div class="toolbar">
      <el-button type="primary" @click="showDialog = true">新增机构</el-button>
    </div>
    <el-table :data="partners" stripe style="width: 100%">
      <el-table-column prop="name" label="机构名称" />
      <el-table-column prop="students" label="学生数" width="120" />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="row.status === 'ACTIVE' ? 'success' : 'info'">
            {{ row.status === 'ACTIVE' ? '合作中' : '待审核' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button type="primary" link>编辑</el-button>
          <el-button type="danger" link>删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showDialog" title="新增合作机构" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="机构名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="form.contact" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.phone" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submit">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { adminApi } from '../apis/admin'
import { ElMessage } from 'element-plus'

const showDialog = ref(false)
const partners = ref<any[]>([])
const form = reactive({ name: '', contact: '', phone: '' })

onMounted(async () => {
  try {
    const res = await adminApi.getPartners()
    partners.value = res.data
  } catch (e) {
    console.error('加载机构列表失败', e)
  }
})

async function submit() {
  try {
    await adminApi.createPartner(form)
    ElMessage.success('机构已创建')
    showDialog.value = false
  } catch (e) {
    ElMessage.error('创建失败')
  }
}
</script>

<style scoped>
.toolbar { margin-bottom: 16px; }
</style>