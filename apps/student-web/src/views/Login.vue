<template>
  <div class="login-page">
    <div class="login-card">
      <div class="logo-area">
        <div class="logo-icon">🧠</div>
        <h1>BrainSpark</h1>
        <p>认知训练小达人</p>
      </div>
      <div class="login-form">
        <input v-model="studentCode" placeholder="输入学生码" class="big-input" @keyup.enter="handleLogin" />
        <button class="big-button" @click="handleLogin" :disabled="loading">
          {{ loading ? '登录中...' : '开始训练' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const studentCode = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!studentCode.value.trim()) return
  loading.value = true
  try {
    await userStore.login(studentCode.value, 'student123')
    router.push('/')
  } catch (e) {
    alert('登录失败，请检查学生码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex; justify-content: center; align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  text-align: center; padding: 40px;
  background: rgba(255,255,255,0.95);
  border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  width: 360px;
}
.logo-icon { font-size: 64px; margin-bottom: 10px; }
.logo-area h1 { font-size: 28px; color: #333; margin: 0; }
.logo-area p { color: #666; margin: 8px 0 24px; }
.big-input {
  width: 100%; padding: 16px 20px; font-size: 20px;
  border: 2px solid #e0e0e0; border-radius: 12px;
  outline: none; box-sizing: border-box;
  text-align: center; letter-spacing: 4px;
}
.big-input:focus { border-color: #667eea; }
.big-button {
  width: 100%; padding: 16px; margin-top: 16px;
  font-size: 20px; font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; border: none; border-radius: 12px;
  cursor: pointer; transition: transform 0.2s;
}
.big-button:hover { transform: scale(1.02); }
.big-button:disabled { opacity: 0.6; cursor: not-allowed; }
</style>