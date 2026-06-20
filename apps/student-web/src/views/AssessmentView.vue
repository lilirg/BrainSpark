<template>
  <div class="assessment">
    <div class="assessment-header">
      <h2>{{ task?.title || '测评中' }}</h2>
      <div class="timer">{{ formattedTime }}</div>
    </div>
    <div ref="gameContainer" class="game-container"></div>
    <div v-if="showResult" class="result-overlay">
      <div class="result-card">
        <div class="result-icon">⭐</div>
        <h2>太棒了！</h2>
        <p>得分: {{ gameScore }}</p>
        <p>用时: {{ gameTime }}</p>
        <button class="big-button" @click="goHome">返回首页</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssessmentStore } from '../stores/assessment'
import { SchulteGridGame } from '../engines/SchulteGridGame'
import { EventCollector } from '../engines/EventCollector'
import { TimeGuard } from '../engines/TimeGuard'

const route = useRoute()
const router = useRouter()
const assessmentStore = useAssessmentStore()
const gameContainer = ref<HTMLDivElement>()
const showResult = ref(false)
const gameScore = ref(0)
const gameTime = ref('')
const elapsedSeconds = ref(0)

const task = computed(() => assessmentStore.currentTask)
const formattedTime = computed(() => {
  const m = Math.floor(elapsedSeconds.value / 60)
  const s = elapsedSeconds.value % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})

function goHome() {
  router.push('/')
}

let game: SchulteGridGame | null = null
let eventCollector: EventCollector | null = null
let timeGuard: TimeGuard | null = null
let timerInterval: ReturnType<typeof setInterval> | null = null

onMounted(async () => {
  const taskId = Number(route.params.id)
  await assessmentStore.startTask(taskId)

  if (gameContainer.value) {
    // 初始化事件采集器
    eventCollector = new EventCollector('student-1', `session-${Date.now()}`)
    eventCollector.start()

    // 初始化防沉迷
    timeGuard = new TimeGuard()
    timeGuard.setCallback((event, data) => {
      if (event === 'limit_reached' || event === 'night_time') {
        game?.pause()
        alert(data?.message || '使用时间已到')
      }
    })
    timeGuard.start()

    // 初始化游戏
    game = new SchulteGridGame({
      width: gameContainer.value.clientWidth,
      height: 600,
      gridSize: 5,
      theme: 'space',
      ageGroup: '9-11'
    })

    gameContainer.value.appendChild(game.view)
    await game.init()

    // 设置事件回调
    game.setEventCallback((event) => {
      eventCollector?.collect({
        type: event.type as any,
        timestamp: event.timestamp,
        data: event.data
      })
    })

    // 启动游戏
    game.start()

    // 计时器
    timerInterval = setInterval(() => {
      elapsedSeconds.value++
      game?.updateScore()
    }, 1000)
  }
})

onUnmounted(() => {
  timerInterval && clearInterval(timerInterval)
  eventCollector?.stop()
  timeGuard?.stop()
  game?.destroy()
})
</script>

<style scoped>
.assessment { height: 100vh; display: flex; flex-direction: column; }
.assessment-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 24px; background: #1a1a2e; color: white;
}
.assessment-header h2 { margin: 0; font-size: 20px; }
.timer { font-size: 24px; font-weight: bold; font-family: monospace; }
.game-container { flex: 1; display: flex; justify-content: center; align-items: center; background: #0a0a2e; }
.result-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.7); display: flex;
  justify-content: center; align-items: center; z-index: 1000;
}
.result-card {
  background: white; border-radius: 20px; padding: 40px;
  text-align: center; max-width: 360px;
}
.result-icon { font-size: 64px; margin-bottom: 16px; }
.result-card h2 { color: #333; margin-bottom: 12px; }
.result-card p { color: #666; margin: 8px 0; }
.big-button {
  margin-top: 20px; padding: 12px 32px; font-size: 18px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; border: none; border-radius: 12px; cursor: pointer;
}
</style>