<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <div class="header-left">
        <span class="logo">BrainSpark</span>
        <span class="subtitle">家长端</span>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            {{ userStore.user?.username || '家长' }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="settings">设置</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-container>
      <el-aside width="220px" class="layout-aside">
        <el-menu
          :default-active="route.path"
          router
          class="aside-menu"
        >
          <el-menu-item index="/dashboard">
            <el-icon><DataBoard /></el-icon>
            <span>仪表板</span>
          </el-menu-item>
          <el-menu-item index="/reports">
            <el-icon><Document /></el-icon>
            <span>报告中心</span>
          </el-menu-item>
          <el-menu-item index="/growth">
            <el-icon><TrendCharts /></el-icon>
            <span>成长追踪</span>
          </el-menu-item>
          <el-menu-item index="/subscription">
            <el-icon><Coin /></el-icon>
            <span>订阅管理</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ArrowDown, DataBoard, Document, TrendCharts, Coin, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

function handleCommand(command: string) {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  } else if (command === 'settings') {
    router.push('/settings')
  }
}
</script>

<style scoped>
.layout-container { height: 100vh; }
.layout-header {
  display: flex; align-items: center; justify-content: space-between;
  background: #fff; border-bottom: 1px solid #e4e7ed; padding: 0 20px;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.logo { font-size: 20px; font-weight: 700; color: #409eff; }
.subtitle { font-size: 14px; color: #909399; }
.user-info { cursor: pointer; display: flex; align-items: center; gap: 4px; }
.layout-aside { background: #fff; border-right: 1px solid #e4e7ed; }
.aside-menu { border-right: none; }
.layout-main { background: #f5f7fa; padding: 20px; }
</style>