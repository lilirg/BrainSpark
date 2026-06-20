<template>
  <div class="notification-mgmt">
    <h2>通知管理</h2>
    <el-card>
      <el-form :model="form" label-width="100px">
        <el-form-item label="通知标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="通知内容">
          <el-input v-model="form.content" type="textarea" :rows="6" />
        </el-form-item>
        <el-form-item label="发送对象">
          <el-select v-model="form.target" multiple placeholder="选择发送对象">
            <el-option label="所有家长" value="PARENT" />
            <el-option label="所有教师" value="TEACHER" />
            <el-option label="所有学生" value="STUDENT" />
          </el-select>
        </el-form-item>
        <el-form-item label="发送方式">
          <el-checkbox-group v-model="form.channels">
            <el-checkbox label="APP_PUSH">App 推送</el-checkbox>
            <el-checkbox label="SMS">短信</el-checkbox>
            <el-checkbox label="EMAIL">邮件</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="send">发送通知</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { adminApi } from '../apis/admin'
import { ElMessage } from 'element-plus'

const form = reactive({
  title: '',
  content: '',
  target: [],
  channels: ['APP_PUSH']
})

async function send() {
  try {
    await adminApi.sendNotification(form)
    ElMessage.success('通知已发送')
    form.title = ''
    form.content = ''
  } catch (e) {
    ElMessage.error('发送失败')
  }
}
</script>