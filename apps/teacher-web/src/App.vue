<template>
  <el-container>
    <el-header>
      <div class="header-content">
        <h1>BrainSpark 教师端</h1>
        <el-space>
          <el-dropdown>
            <span class="el-dropdown-link">
              {{ userName }} <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人中心</el-dropdown-item>
                <el-dropdown-item divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-space>
      </div>
    </el-header>
    <el-container>
      <el-aside width="200px">
        <el-menu :default-active="activeMenu" router>
          <el-menu-item index="/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据看板</span>
          </el-menu-item>
          <el-menu-item index="/class">
            <el-icon><UserFilled /></el-icon>
            <span>班级管理</span>
          </el-menu-item>
          <el-menu-item index="/assessment">
            <el-icon><Checked /></el-icon>
            <span>测评管理</span>
          </el-menu-item>
          <el-menu-item index="/reports">
            <el-icon><Document /></el-icon>
            <span>报告查看</span>
          </el-menu-item>
          <el-menu-item index="/students">
            <el-icon><User /></el-icon>
            <span>学生档案</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  DataAnalysis,
  UserFilled,
  Checked,
  Document,
  User,
  ArrowDown,
} from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = ref(route.path)
const userName = ref('王老师')

// 监听路由变化
watch(
  () => route.path,
  (path) => {
    activeMenu.value = path
  }
)
</script>

<style scoped>
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header-content h1 {
  margin: 0;
  font-size: 18px;
  color: #409eff;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>