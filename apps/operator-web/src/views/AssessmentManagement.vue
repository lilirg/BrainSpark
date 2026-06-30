<template>
  <div class="assessment-mgmt">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>测评管理</span>
          <el-button type="primary" @click="handleAdd">新增测评</el-button>
        </div>
      </template>

      <el-table :data="assessments" stripe v-loading="loading">
        <el-table-column prop="name" label="测评名称" />
        <el-table-column prop="type" label="类型" width="150">
          <template #default="{ row }">
            <el-tag>{{ row.typeCode }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="durationMin" label="时长(分钟)" width="120" />
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
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" :title="isEdit ? '编辑测评' : '新增测评'" width="600px" @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="测评名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入测评名称" />
        </el-form-item>
        <el-form-item label="测评类型" prop="typeCode">
          <el-select v-model="form.typeCode" placeholder="请选择测评类型" style="width: 100%">
            <el-option label="舒尔特方格" value="SCHULTE_GRID" />
            <el-option label="数字广度" value="NUMBER_SPAN" />
            <el-option label="模式识别" value="PATTERN_RECOGNITION" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入测评描述" />
        </el-form-item>
        <el-form-item label="时长(分钟)" prop="durationMin">
          <el-input-number v-model="form.durationMin" :min="5" :max="60" :step="5" />
        </el-form-item>
        <el-form-item label="难度" prop="difficulty">
          <el-select v-model="form.difficulty" placeholder="请选择难度" style="width: 100%">
            <el-option label="简单" value="EASY" />
            <el-option label="中等" value="MEDIUM" />
            <el-option label="困难" value="HARD" />
          </el-select>
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
import { adminApi } from '../apis/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

interface AssessmentItem {
  id: number
  name: string
  typeCode: string
  description: string
  durationMin: number
  difficulty: string
  status: string
  createdAt: string
}

const assessments = ref<AssessmentItem[]>([])
const loading = ref(false)
const showDialog = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = ref({
  name: '',
  typeCode: '',
  description: '',
  durationMin: 15,
  difficulty: 'MEDIUM',
  id: 0
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入测评名称', trigger: 'blur' }],
  typeCode: [{ required: true, message: '请选择测评类型', trigger: 'change' }]
}

async function loadAssessments() {
  loading.value = true
  try {
    const res = await adminApi.getAssessments()
    assessments.value = res.data ?? []
  } catch (e) {
    console.error('加载测评列表失败', e)
    ElMessage.error('加载测评列表失败')
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  isEdit.value = false
  form.value = { name: '', typeCode: '', description: '', durationMin: 15, difficulty: 'MEDIUM', id: 0 }
  showDialog.value = true
}

function handleEdit(row: AssessmentItem) {
  isEdit.value = true
  form.value = {
    name: row.name,
    typeCode: row.typeCode,
    description: row.description,
    durationMin: row.durationMin,
    difficulty: row.difficulty,
    id: row.id
  }
  showDialog.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    submitting.value = true
    try {
      if (isEdit.value) {
        await adminApi.updateAssessment(form.value.id, form.value)
        ElMessage.success('更新成功')
      } else {
        await adminApi.createAssessment(form.value)
        ElMessage.success('创建成功')
      }
      showDialog.value = false
      await loadAssessments()
    } catch (e) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

async function toggleStatus(id: number, active: boolean) {
  try {
    await adminApi.updateAssessmentStatus(id, active ? 'ACTIVE' : 'INACTIVE')
    ElMessage.success('状态已更新')
    await loadAssessments()
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

async function handleDelete(row: AssessmentItem) {
  try {
    await ElMessageBox.confirm(`确定删除测评 "${row.name}" 吗？`, '确认删除', { type: 'warning' })
    await adminApi.deleteAssessment(row.id)
    ElMessage.success('删除成功')
    await loadAssessments()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

function resetForm() {
  formRef.value?.resetFields()
}

onMounted(() => {
  loadAssessments()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>