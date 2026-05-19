<template>
  <div class="class-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>班级管理</span>
          <el-button type="primary" @click="showAddDialog = true">
            新增班级
          </el-button>
        </div>
      </template>

      <el-table :data="classes" style="width: 100%">
        <el-table-column prop="name" label="班级名称" />
        <el-table-column prop="studentCount" label="学生人数" />
        <el-table-column prop="grade" label="年级" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button size="small">查看</el-button>
            <el-button size="small" type="primary">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" title="新增班级" width="400px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="班级名称">
          <el-input v-model="form.name" placeholder="请输入班级名称" />
        </el-form-item>
        <el-form-item label="年级">
          <el-select v-model="form.grade" placeholder="请选择年级">
            <el-option label="一年级" value="1" />
            <el-option label="二年级" value="2" />
            <el-option label="三年级" value="3" />
            <el-option label="四年级" value="4" />
            <el-option label="五年级" value="5" />
            <el-option label="六年级" value="6" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface ClassItem {
  id: number
  name: string
  studentCount: number
  grade: string
}

const classes = ref<ClassItem[]>([
  { id: 1, name: '一年级三班', studentCount: 35, grade: '1' },
  { id: 2, name: '二年级一班', studentCount: 32, grade: '2' },
  { id: 3, name: '三年级五班', studentCount: 38, grade: '3' },
])

const showAddDialog = ref(false)
const form = ref({ name: '', grade: '' })
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>