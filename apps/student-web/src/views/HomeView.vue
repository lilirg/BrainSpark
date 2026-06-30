<template>
  <div class="home">
    <header class="home-header">
      <h1>今日任务</h1>
      <div class="time-info">
        <span>已用: {{ usedTime }}分钟</span>
        <span>剩余: {{ remainingTime }}分钟</span>
      </div>
    </header>

    <div class="task-grid">
      <div v-for="task in tasks" :key="task.id" class="task-card" @click="startTask(task.id)">
        <div class="task-icon">{{ getTaskIcon(task.type) }}</div>
        <div class="task-name">{{ task.title }}</div>
        <div class="task-desc">{{ task.description }}</div>
        <div class="task-status" :class="task.status">
          {{ task.status === 'PENDING' ? '未开始' : task.status === 'IN_PROGRESS' ? '进行中' : '已完成' }}
        </div>
      </div>
    </div>

    <div v-if="!canPlay" class="time-limit-overlay">
      <div class="time-limit-card">
        <div class="limit-icon">⏰</div>
        <h2>休息时间到啦！</h2>
        <p>{{ limitMessage }}</p>
        <button class="big-button" @click="goHome">返回</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAssessmentStore } from '../stores/assessment'
import { TimeGuard } from '../engines/TimeGuard'

const router = useRouter()
const assessmentStore = useAssessmentStore()
const tasks = ref<any[]>([])
const canPlay = ref(true)
const limitMessage = ref('')
const usedTime = ref(0)
const remainingTime = ref(40)

const timeGuard = new TimeGuard()

onMounted(async () => {
  await assessmentStore.fetchTodayTasks()
  tasks.value = assessmentStore.todayTasks

  timeGuard.setCallback((event, data) => {
    if (event === 'night_time' || event === 'limit_reached') {
      canPlay.value = false
      limitMessage.value = data?.message || ''
    }
  })
  timeGuard.start()
})

onUnmounted(() => {
  timeGuard.stop()
})

function getTaskIcon(type: string): string {
  const icons: Record<string, string> = {
    SCHULTE_GRID: '🔢',
    NUMBER_SPAN: '🔢',
    PATTERN_RECOGNITION: '🧩'
  }
  return icons[type] || '🎮'
}

async function startTask(id: number) {
  if (!canPlay.value) return
  await assessmentStore.startTask(id)
  router.push(`/assessment/${id}`)
}

function goHome() {
  canPlay.value = true
}
</script>

<style scoped>
.home { padding: 20px; max-width: 800px; margin: 0 auto; }
.home-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.home-header h1 { font-size: 24px; color: #333; }
.time-info { display: flex; gap: 16px; color: #666; font-size: 14px; }
.task-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; }
.task-card {
  background: white; border-radius: 16px; padding: 20px;
  text-align: center; cursor: pointer;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}
.task-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.15); }
.task-icon { font-size: 48px; margin-bottom: 12px; }
.task-name { font-size: 18px; font-weight: 600; color: #333; margin-bottom: 8px; }
.task-desc { font-size: 14px; color: #666; margin-bottom: 12px; }
.task-status { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; }
.task-status.PENDING { background: #fff3e0; color: #e65100; }
.task-status.IN_PROGRESS { background: #e3f2fd; color: #1565c0; }
.task-status.COMPLETED { background: #e8f5e9; color: #2e7d32; }
.time-limit-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6); display: flex;
  justify-content: center; align-items: center; z-index: 1000;
}
.time-limit-card {
  background: white; border-radius: 20px; padding: 40px;
  text-align: center; max-width: 360px;
}
.limit-icon { font-size: 64px; margin-bottom: 16px; }
.time-limit-card h2 { color: #333; margin-bottom: 12px; }
.time-limit-card p { color: #666; margin-bottom: 24px; }
.big-button {
  padding: 12px 32px; font-size: 18px; font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; border: none; border-radius: 12px; cursor: pointer;
}
</style>