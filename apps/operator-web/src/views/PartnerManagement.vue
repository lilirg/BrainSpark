<template>
  <div class="partner-mgmt">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>机构合作管理</span>
          <el-button type="primary" @click="handleAdd">新增机构</el-button>
        </div>
      </template>

      <el-table :data="partners" stripe v-loading="loading">
        <el-table-column prop="name" label="机构名称" />
        <el-table-column prop="contact" label="联系人" width="120" />
        <el-table-column prop="phone" label="联系电话" width="130" />
        <el-table-column prop="students" label="学生数" width="100">
          <template #default="{ row }">
            <span class="student-count">{{ row.students }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'ACTIVE' ? 'success' : 'info'">
              {{ row.status === 'ACTIVE' ? '合作中' : '待审核' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" :title="isEdit ? '编辑机构' : '新增机构'" width="500px" @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="机构名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入机构名称" />
        </el-form-item>
        <el-form-item label="联系人" prop="contact">
          <el-input v-model="form.contact" placeholder="请输入联系人" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi, type PartnerItem } from '../apis/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const partners = ref<PartnerItem[]>([])
const loading = ref(false)
const showDialog = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = ref({
  name: '',
  contact: '',
  phone: '',
  email: '',
  students: 0,
  status: 'PENDING',
  id: 0
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入机构名称', trigger: 'blur' }],
  contact: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
}

async function loadPartners() {
  loading.value = true
  try {
    const res = await adminApi.getPartners()
    partners.value = res.data ?? []
  } catch (e) {
    console.error('加载机构列表失败', e)
    ElMessage.error('加载机构列表失败')
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  isEdit.value = false
  form.value = { name: '', contact: '', phone: '', email: '', students: 0, status: 'PENDING', id: 0 }
  showDialog.value = true
}

function handleEdit(row: PartnerItem) {
  isEdit.value = true
  form.value = { ...row }
  showDialog.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    submitting.value = true
    try {
      if (isEdit.value) {
        await adminApi.updatePartner(form.value.id, form.value)
        ElMessage.success('更新成功')
      } else {
        await adminApi.createPartner(form.value)
        ElMessage.success('创建成功')
      }
      showDialog.value = false
      await loadPartners()
    } catch (e) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

async function handleDelete(row: PartnerItem) {
  try {
    await ElMessageBox.confirm(`确定删除机构 "${row.name}" 吗？`, '确认删除', { type: 'warning' })
    await adminApi.deletePartner(row.id)
    ElMessage.success('删除成功')
    await loadPartners()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

function resetForm() {
  formRef.value?.resetFields()
}

onMounted(() => {
  loadPartners()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.student-count {
  font-weight: 600;
  color: #409eff;
}
</style>