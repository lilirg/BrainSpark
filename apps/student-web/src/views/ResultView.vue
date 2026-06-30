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
import { useAssessmentStore } from '../stores/assessment'

const router = useRouter()
const assessmentStore = useAssessmentStore()

const score = ref(0)
const time = ref('0秒')
const accuracy = ref(0)
const level = ref('待评定')

const encourageTexts: Record<string, string[]> = {
  EXCELLENT: [
    '你做得非常棒！继续保持！',
    '今天又进步了，真厉害！',
    '你的专注力越来越好了！',
    '太厉害了，继续加油哦！'
  ],
  GOOD: [
    '表现不错！继续努力！',
    '你越来越棒了！',
    '坚持下去，你会更优秀的！',
    '加油，你可以做到更好的！'
  ],
  AVERAGE: [
    '继续加油，你会越来越好的！',
    '每天进步一点点！',
    '不要放弃，坚持训练！',
    '相信自己，你可以的！'
  ]
}

const encourageText = ref('')

function calculateLevel(s: number): string {
  if (s >= 90) return 'EXCELLENT'
  if (s >= 70) return 'GOOD'
  return 'AVERAGE'
}

onMounted(() => {
  if (assessmentStore.result) {
    score.value = assessmentStore.result.overallScore ?? 0
    time.value = `${assessmentStore.result.duration ?? 0}秒`
    accuracy.value = assessmentStore.result.accuracy ?? 0
    level.value = assessmentStore.result.level ?? '待评定'
    
    const levelKey = calculateLevel(score.value)
    const texts = encourageTexts[levelKey]
    encourageText.value = texts?.[Math.floor(Math.random() * texts.length)] ?? '继续加油！'
  }
})

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