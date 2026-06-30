<template>
  <div class="class-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>班级管理</span>
          <el-button type="primary" @click="handleAdd">
            新增班级
          </el-button>
        </div>
      </template>

      <el-table :data="classes" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="班级名称" />
        <el-table-column prop="grade" label="年级" />
        <el-table-column prop="maxStudents" label="最大人数" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.isActive ? 'success' : 'info'">
              {{ row.isActive ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" :title="isEdit ? '编辑班级' : '新增班级'" width="400px" @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="班级名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入班级名称" />
        </el-form-item>
        <el-form-item label="年级" prop="grade">
          <el-select v-model="form.grade" placeholder="请选择年级" style="width: 100%">
            <el-option v-for="i in 6" :key="i" :label="`${i}年级`" :value="`${i}`" />
          </el-select>
        </el-form-item>
        <el-form-item label="最大人数" prop="maxStudents">
          <el-input-number v-model="form.maxStudents" :min="10" :max="100" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入班级描述" />
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
import { classApi, type ClassItem, type ClassRequest } from '../apis/class'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const classes = ref<ClassItem[]>([])
const loading = ref(false)
const showDialog = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = ref<ClassRequest>({
  name: '',
  grade: '',
  description: '',
  maxStudents: 50
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }],
  grade: [{ required: true, message: '请选择年级', trigger: 'change' }]
}

async function loadClasses() {
  loading.value = true
  try {
    const res = await classApi.getClasses()
    classes.value = res.content ?? []
  } catch (e) {
    console.error('加载班级列表失败', e)
    ElMessage.error('加载班级列表失败')
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  isEdit.value = false
  form.value = { name: '', grade: '', description: '', maxStudents: 50 }
  showDialog.value = true
}

function handleEdit(row: ClassItem) {
  isEdit.value = true
  form.value = {
    name: row.name,
    grade: row.grade,
    description: row.description ?? '',
    maxStudents: row.maxStudents
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
        await classApi.updateClass(0, form.value)
        ElMessage.success('更新成功')
      } else {
        await classApi.createClass(form.value)
        ElMessage.success('创建成功')
      }
      showDialog.value = false
      await loadClasses()
    } catch (e) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

async function handleDelete(row: ClassItem) {
  try {
    await ElMessageBox.confirm(`确定删除班级 "${row.name}" 吗？`, '确认删除', { type: 'warning' })
    await classApi.deleteClass(row.id)
    ElMessage.success('删除成功')
    await loadClasses()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

function resetForm() {
  formRef.value?.resetFields()
}

onMounted(() => {
  loadClasses()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>