<template>
  <div class="subscription">
    <h2>订阅管理</h2>
    <el-row :gutter="20">
      <el-col :span="8" v-for="plan in plans" :key="plan.name">
        <el-card :class="['plan-card', { 'plan-recommended': plan.recommended }]" shadow="hover">
          <div v-if="plan.recommended" class="recommended-badge">推荐</div>
          <h3 class="plan-name">{{ plan.name }}</h3>
          <div class="plan-price">
            <span class="price">¥{{ plan.price }}</span>
            <span class="period">/{{ plan.period }}</span>
          </div>
          <ul class="plan-features">
            <li v-for="feature in plan.features" :key="feature">{{ feature }}</li>
          </ul>
          <el-button type="primary" class="plan-btn" :disabled="plan.current">
            {{ plan.current ? '当前订阅' : '立即订阅' }}
          </el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
const plans = [
  {
    name: '基础版', price: 0, period: '永久',
    features: ['基础测评报告', '月度成长追踪', '基础认知训练'],
    current: true, recommended: false
  },
  {
    name: '高级版', price: 99, period: '月',
    features: ['高级测评报告', 'AI 个性化建议', '周度成长追踪', '专属客服'],
    current: false, recommended: true
  },
  {
    name: '尊享版', price: 499, period: '年',
    features: ['全部高级版功能', '专家一对一咨询', '年度成长总结', '优先体验新功能'],
    current: false, recommended: false
  }
]
</script>

<style scoped>
.plan-card { text-align: center; position: relative; padding: 20px 0; }
.plan-recommended { border: 2px solid #409eff; }
.recommended-badge {
  position: absolute; top: 0; right: 0;
  background: #409eff; color: #fff; padding: 4px 12px;
  border-radius: 0 4px 0 4px; font-size: 12px;
}
.plan-name { font-size: 20px; margin-bottom: 16px; }
.plan-price { margin-bottom: 20px; }
.price { font-size: 36px; font-weight: 700; color: #409eff; }
.period { font-size: 14px; color: #909399; }
.plan-features { list-style: none; padding: 0; margin-bottom: 20px; }
.plan-features li { padding: 8px 0; color: #606266; }
.plan-btn { width: 80%; }
</style>