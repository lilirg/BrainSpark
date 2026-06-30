<template>
  <div class="knowledge-mgmt">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>知识库管理</span>
          <div>
            <el-button type="primary" @click="handleAdd">新增文档</el-button>
            <el-button type="warning" @click="reindex" :loading="reindexing">重建索引</el-button>
          </div>
        </div>
      </template>

      <el-table :data="docs" stripe v-loading="loading">
        <el-table-column prop="title" label="文档名称" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="索引状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'INDEXED' ? 'success' : 'warning'">
              {{ row.status === 'INDEXED' ? '已索引' : '待索引' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column prop="updatedAt" label="更新时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" :title="isEdit ? '编辑文档' : '新增文档'" width="600px" @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="文档名称" prop="title">
          <el-input v-model="form.title" placeholder="请输入文档名称" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
            <el-option label="认知科学" value="COGNITIVE_SCIENCE" />
            <el-option label="教育理论" value="EDUCATION_THEORY" />
            <el-option label="测评方法" value="ASSESSMENT_METHOD" />
            <el-option label="训练指南" value="TRAINING_GUIDE" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="8" placeholder="请输入文档内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="viewDialog" title="文档详情" width="700px">
      <div class="doc-view">
        <h3>{{ viewDoc.title }}</h3>
        <el-tag>{{ viewDoc.category }}</el-tag>
        <el-tag :type="viewDoc.status === 'INDEXED' ? 'success' : 'warning'">
          {{ viewDoc.status === 'INDEXED' ? '已索引' : '待索引' }}
        </el-tag>
        <p>{{ viewDoc.content }}</p>
      </div>
      <template #footer>
        <el-button @click="viewDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi, type KnowledgeDoc } from '../apis/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const docs = ref<KnowledgeDoc[]>([])
const loading = ref(false)
const reindexing = ref(false)
const showDialog = ref(false)
const viewDialog = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const viewDoc = ref<KnowledgeDoc>({} as KnowledgeDoc)

const form = ref({
  title: '',
  category: '',
  content: '',
  status: 'PENDING',
  id: 0,
  createdAt: '',
  updatedAt: ''
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入文档名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  content: [{ required: true, message: '请输入文档内容', trigger: 'blur' }]
}

async function loadDocs() {
  loading.value = true
  try {
    const res = await adminApi.getKnowledgeDocs()
    docs.value = res.data ?? []
  } catch (e) {
    console.error('加载知识库失败', e)
    ElMessage.error('加载知识库失败')
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  isEdit.value = false
  form.value = { title: '', category: '', content: '', status: 'PENDING', id: 0, createdAt: '', updatedAt: '' }
  showDialog.value = true
}

function handleView(row: KnowledgeDoc) {
  viewDoc.value = row
  viewDialog.value = true
}

function handleEdit(row: KnowledgeDoc) {
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
        await adminApi.updateKnowledgeDoc(form.value.id, form.value)
        ElMessage.success('更新成功')
      } else {
        await adminApi.createKnowledgeDoc(form.value)
        ElMessage.success('创建成功')
      }
      showDialog.value = false
      await loadDocs()
    } catch (e) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

async function handleDelete(row: KnowledgeDoc) {
  try {
    await ElMessageBox.confirm(`确定删除文档 "${row.title}" 吗？`, '确认删除', { type: 'warning' })
    await adminApi.deleteKnowledgeDoc(row.id)
    ElMessage.success('删除成功')
    await loadDocs()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

async function reindex() {
  reindexing.value = true
  try {
    await adminApi.reindexKnowledge()
    ElMessage.success('重建任务已提交')
  } catch (e) {
    ElMessage.error('重建失败')
  } finally {
    reindexing.value = false
  }
}

function resetForm() {
  formRef.value?.resetFields()
}

onMounted(() => {
  loadDocs()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.doc-view {
  padding: 10px;
}
.doc-view h3 {
  margin: 0 0 10px;
  color: #409eff;
}
.doc-view el-tag {
  margin-right: 10px;
}
.doc-view p {
  margin-top: 16px;
  line-height: 1.8;
  color: #606266;
  white-space: pre-wrap;
}
</style>