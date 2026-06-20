<template>
  <div class="result-page">
    <div class="result-container">
      <div class="stars">⭐⭐⭐</div>
      <h1>测评完成！</h1>
      <div class="score-circle">
        <div class="score-value">{{ score }}</div>
        <div class="score-label">分</div>
      </div>
      <div class="result-details">
        <div class="detail-item">
          <span class="label">用时</span>
          <span class="value">{{ time }}</span>
        </div>
        <div class="detail-item">
          <span class="label">正确率</span>
          <span class="value">{{ accuracy }}%</span>
        </div>
        <div class="detail-item">
          <span class="label">等级</span>
          <span class="value">{{ level }}</span>
        </div>
      </div>
      <p class="encourage-text">{{ encourageText }}</p>
      <button class="big-button" @click="goHome">返回首页</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const score = ref(85)
const time = ref('45.2秒')
const accuracy = ref(92)
const level = ref('优秀')

const encourageTexts = [
  '你做得非常棒！继续保持！',
  '今天又进步了，真厉害！',
  '你的专注力越来越好了！',
  '太厉害了，继续加油哦！'
]

const encourageText = ref(encourageTexts[Math.floor(Math.random() * encourageTexts.length)])

function goHome() {
  router.push('/')
}
</script>

<style scoped>
.result-page {
  display: flex; justify-content: center; align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.result-container {
  text-align: center; padding: 40px;
  background: rgba(255,255,255,0.95);
  border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  width: 400px;
}
.stars { font-size: 48px; margin-bottom: 10px; }
h1 { color: #333; margin: 0 0 24px; }
.score-circle {
  width: 120px; height: 120px; border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex; flex-direction: column; justify-content: center;
  align-items: center; margin: 0 auto 24px;
}
.score-value { font-size: 36px; font-weight: bold; color: white; }
.score-label { font-size: 14px; color: rgba(255,255,255,0.8); }
.result-details { margin-bottom: 20px; }
.detail-item {
  display: flex; justify-content: space-between;
  padding: 8px 0; border-bottom: 1px solid #eee;
}
.label { color: #666; }
.value { font-weight: 600; color: #333; }
.encourage-text { color: #667eea; font-size: 16px; margin-bottom: 24px; }
.big-button {
  padding: 12px 32px; font-size: 18px; font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; border: none; border-radius: 12px; cursor: pointer;
}
</style>