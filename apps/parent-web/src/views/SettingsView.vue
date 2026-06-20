<template>
  <div class="settings">
    <h2>设置</h2>
    <el-card>
      <el-form :model="settings" label-width="140px">
        <el-divider>通知设置</el-divider>
        <el-form-item label="每日报告">
          <el-switch v-model="settings.dailyReport" />
        </el-form-item>
        <el-form-item label="每周报告">
          <el-switch v-model="settings.weeklyReport" />
        </el-form-item>
        <el-form-item label="测评提醒">
          <el-switch v-model="settings.assessmentReminder" />
        </el-form-item>
        <el-form-item label="成长预警">
          <el-switch v-model="settings.growthAlert" />
        </el-form-item>
        <el-divider>使用限制</el-divider>
        <el-form-item label="每日使用时长">
          <el-input-number v-model="settings.dailyTimeLimit" :min="15" :max="120" :step="15" /> 分钟
        </el-form-item>
        <el-form-item label="夜间禁用时段">
          <el-time-picker v-model="nightTime" is-range range-separator="至" start-placeholder="开始" end-placeholder="结束" format="HH:mm" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { parentApi } from '../apis/parent'
import { ElMessage } from 'element-plus'

const settings = reactive({
  dailyReport: true,
  weeklyReport: true,
  assessmentReminder: true,
  growthAlert: false,
  dailyTimeLimit: 30
})

const nightTime = ref([new Date(2024, 0, 1, 22, 0), new Date(2024, 0, 2, 6, 0)])

async function saveSettings() {
  try {
    await parentApi.updateSettings(settings)
    ElMessage.success('设置已保存')
  } catch (e) {
    ElMessage.error('保存失败')
  }
}
</script>