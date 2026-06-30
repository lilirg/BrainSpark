# 前台应用开发计划

> 生成时间: 2026-06-30
> 状态: 待执行

## 一、前台应用现状分析

### 1.1 应用清单

| 应用 | 路径 | 状态 | 完成度 |
|------|------|------|--------|
| 学生端 (student-web) | `apps/student-web/` | ✅ 基本完成 | 85% |
| 家长端 (parent-web) | `apps/parent-web/` | ✅ 基本完成 | 80% |
| 教师端 (teacher-web) | `apps/teacher-web/` | ✅ 基本完成 | 75% |
| 运营端 (operator-web) | `apps/operator-web/` | ⚠️ 部分完成 | 50% |

### 1.2 学生端 (student-web) - 完成度 85%

**已完成:**
- [x] 登录页面 ([`Login.vue`](apps/student-web/src/views/Login.vue))
- [x] 任务首页 ([`HomeView.vue`](apps/student-web/src/views/HomeView.vue))
- [x] 测评游戏页面 ([`AssessmentView.vue`](apps/student-web/src/views/AssessmentView.vue))
- [x] 结果展示页面 ([`ResultView.vue`](apps/student-web/src/views/ResultView.vue))
- [x] SchulteGrid 游戏引擎 ([`SchulteGridGame.ts`](apps/student-web/src/engines/SchulteGridGame.ts))
- [x] 事件采集器 ([`EventCollector.ts`](apps/student-web/src/engines/EventCollector.ts))
- [x] 时间守卫器 ([`TimeGuard.ts`](apps/student-web/src/engines/TimeGuard.ts))
- [x] 路由配置 ([`router/index.ts`](apps/student-web/src/router/index.ts))
- [x] Pinia Store ([`stores/assessment.ts`](apps/student-web/src/stores/assessment.ts), [`stores/user.ts`](apps/student-web/src/stores/user.ts))

**待完善:**
- [ ] 学生端缺少 `index.html` 入口文件检查
- [ ] 游戏引擎仅实现 SchulteGrid，缺少 NumberSpan 和 PatternRecognition 游戏
- [ ] [`ResultView.vue`](apps/student-web/src/views/ResultView.vue:31) 使用硬编码数据，需对接真实 API
- [ ] [`HomeView.vue`](apps/student-web/src/views/HomeView.vue:67) 任务图标映射有 typo (`SCHULTE_GRID` 误写为 `SCHULTE`)
- [ ] 缺少游戏音效和动画反馈
- [ ] 缺少学生端 `public/` 目录下的 favicon 和 manifest

### 1.3 家长端 (parent-web) - 完成度 80%

**已完成:**
- [x] 登录页面 ([`Login.vue`](apps/parent-web/src/views/Login.vue))
- [x] 仪表板 ([`DashboardView.vue`](apps/parent-web/src/views/DashboardView.vue))
- [x] 报告列表 ([`ReportListView.vue`](apps/parent-web/src/views/ReportListView.vue))
- [x] 报告详情 ([`ReportDetailView.vue`](apps/parent-web/src/views/ReportDetailView.vue))
- [x] 成长追踪 ([`GrowthTrackingView.vue`](apps/parent-web/src/views/GrowthTrackingView.vue))
- [x] 订阅管理 ([`SubscriptionView.vue`](apps/parent-web/src/views/SubscriptionView.vue))
- [x] 设置页面 ([`SettingsView.vue`](apps/parent-web/src/views/SettingsView.vue))
- [x] 主布局 ([`MainLayout.vue`](apps/parent-web/src/layouts/MainLayout.vue))
- [x] API 封装 ([`apis/parent.ts`](apps/parent-web/src/apis/parent.ts), [`apis/report.ts`](apps/parent-web/src/apis/report.ts))

**待完善:**
- [ ] [`DashboardView.vue`](apps/parent-web/src/views/DashboardView.vue:48) 统计卡片数据硬编码
- [ ] [`GrowthTrackingView.vue`](apps/parent-web/src/views/GrowthTrackingView.vue:26) 图表数据硬编码，需对接真实 API
- [ ] [`SubscriptionView.vue`](apps/parent-web/src/views/SubscriptionView.vue:26) 订阅方案硬编码，需对接真实 API
- [ ] 缺少家长端 `index.html` 自定义标题
- [ ] 缺少成长追踪的时间范围筛选功能
- [ ] 报告详情页面缺少打印功能

### 1.4 教师端 (teacher-web) - 完成度 75%

**已完成:**
- [x] 登录页面 ([`Login.vue`](apps/teacher-web/src/views/Login.vue))
- [x] 数据看板 ([`Dashboard.vue`](apps/teacher-web/src/views/Dashboard.vue))
- [x] 班级管理 ([`ClassManagement.vue`](apps/teacher-web/src/views/ClassManagement.vue))
- [x] 测评管理 ([`AssessmentList.vue`](apps/teacher-web/src/views/AssessmentList.vue))
- [x] 报告列表 ([`ReportList.vue`](apps/teacher-web/src/views/ReportList.vue))
- [x] 学生档案 ([`StudentProfile.vue`](apps/teacher-web/src/views/StudentProfile.vue))
- [x] 路由配置 ([`router/index.ts`](apps/teacher-web/src/router/index.ts))
- [x] API 封装 ([`apis/assessment.ts`](apps/teacher-web/src/apis/assessment.ts), [`apis/class.ts`](apps/teacher-web/src/apis/class.ts), [`apis/auth.ts`](apps/teacher-web/src/apis/auth.ts))

**待完善:**
- [ ] [`Dashboard.vue`](apps/teacher-web/src/views/Dashboard.vue:71) 统计数据硬编码，需对接真实 API
- [ ] [`StudentProfile.vue`](apps/teacher-web/src/views/StudentProfile.vue:70) 学生数据硬编码，需对接真实 API
- [ ] 缺少班级学生列表的增删改查交互
- [ ] 测评管理缺少创建/编辑/删除测评的完整流程
- [ ] 报告列表缺少筛选和搜索功能
- [ ] 缺少教师端 `index.html` 自定义标题

### 1.5 运营端 (operator-web) - 完成度 50%

**已完成:**
- [x] 登录页面 ([`Login.vue`](apps/operator-web/src/views/Login.vue))
- [x] 仪表板 ([`DashboardView.vue`](apps/operator-web/src/views/DashboardView.vue))
- [x] 测评管理 ([`AssessmentManagement.vue`](apps/operator-web/src/views/AssessmentManagement.vue))
- [x] 知识库管理 ([`KnowledgeManagement.vue`](apps/operator-web/src/views/KnowledgeManagement.vue))
- [x] 合作伙伴管理 ([`PartnerManagement.vue`](apps/operator-web/src/views/PartnerManagement.vue))
- [x] 通知管理 ([`NotificationManagement.vue`](apps/operator-web/src/views/NotificationManagement.vue))
- [x] 主布局 ([`MainLayout.vue`](apps/operator-web/src/layouts/MainLayout.vue))
- [x] 路由配置 ([`router/index.ts`](apps/operator-web/src/router/index.ts))

**待完善:**
- [ ] **缺少 `index.html` 入口文件** - 这是最关键的缺失
- [ ] 缺少 `public/` 目录
- [ ] 缺少 `src/main.ts` 入口文件
- [ ] 缺少 `src/App.vue` 根组件
- [ ] [`DashboardView.vue`](apps/operator-web/src/views/DashboardView.vue) 数据硬编码
- [ ] 所有管理页面缺少完整的 CRUD 交互
- [ ] 缺少运营端 API 封装文件
- [ ] 缺少 stores 状态管理

---

## 二、开发优先级

### P0 - 关键缺失 (必须立即完成)

1. **运营端 (operator-web) 基础架构**
   - 创建 `index.html` 入口文件
   - 创建 `src/main.ts` 入口文件
   - 创建 `src/App.vue` 根组件
   - 配置 Vite 和 TypeScript

### P1 - 数据对接 (提升功能完整性)

2. **学生端数据对接**
   - 对接真实测评任务 API
   - 对接测评结果 API
   - 修复任务图标映射 typo

3. **家长端数据对接**
   - 仪表板统计对接真实 API
   - 成长追踪图表对接真实 API
   - 订阅管理对接真实 API

4. **教师端数据对接**
   - 数据看板对接真实 API
   - 学生档案对接真实 API
   - 班级管理完整 CRUD

### P2 - 功能增强

5. **学生端游戏引擎扩展**
   - 实现 NumberSpan 游戏
   - 实现 PatternRecognition 游戏
   - 添加游戏音效

6. **运营端管理功能增强**
   - 测评管理完整 CRUD
   - 知识库管理完整 CRUD
   - 合作伙伴管理完整 CRUD

---

## 三、开发任务清单

### 任务 1: 运营端基础架构

**目标:** 让运营端可以正常启动运行

**文件清单:**
- [`apps/operator-web/index.html`](apps/operator-web/index.html) - 创建
- [`apps/operator-web/src/main.ts`](apps/operator-web/src/main.ts) - 创建
- [`apps/operator-web/src/App.vue`](apps/operator-web/src/App.vue) - 创建

### 任务 2: 学生端数据对接

**目标:** 学生端所有页面对接真实 API

**修改文件:**
- [`apps/student-web/src/views/ResultView.vue`](apps/student-web/src/views/ResultView.vue)
- [`apps/student-web/src/views/HomeView.vue`](apps/student-web/src/views/HomeView.vue)
- [`apps/student-web/src/apis/assessment.ts`](apps/student-web/src/apis/assessment.ts)

### 任务 3: 家长端数据对接

**目标:** 家长端所有页面对接真实 API

**修改文件:**
- [`apps/parent-web/src/views/DashboardView.vue`](apps/parent-web/src/views/DashboardView.vue)
- [`apps/parent-web/src/views/GrowthTrackingView.vue`](apps/parent-web/src/views/GrowthTrackingView.vue)
- [`apps/parent-web/src/views/SubscriptionView.vue`](apps/parent-web/src/views/SubscriptionView.vue)

### 任务 4: 教师端数据对接

**目标:** 教师端所有页面对接真实 API

**修改文件:**
- [`apps/teacher-web/src/views/Dashboard.vue`](apps/teacher-web/src/views/Dashboard.vue)
- [`apps/teacher-web/src/views/StudentProfile.vue`](apps/teacher-web/src/views/StudentProfile.vue)
- [`apps/teacher-web/src/views/ClassManagement.vue`](apps/teacher-web/src/views/ClassManagement.vue)

### 任务 5: 学生端游戏引擎扩展

**目标:** 实现完整的 3 种测评游戏

**新增文件:**
- [`apps/student-web/src/engines/NumberSpanGame.ts`](apps/student-web/src/engines/NumberSpanGame.ts)
- [`apps/student-web/src/engines/PatternRecognitionGame.ts`](apps/student-web/src/engines/PatternRecognitionGame.ts)

### 任务 6: 运营端管理功能增强

**目标:** 运营端所有管理页面具备完整 CRUD 能力

**修改文件:**
- [`apps/operator-web/src/views/AssessmentManagement.vue`](apps/operator-web/src/views/AssessmentManagement.vue)
- [`apps/operator-web/src/views/KnowledgeManagement.vue`](apps/operator-web/src/views/KnowledgeManagement.vue)
- [`apps/operator-web/src/views/PartnerManagement.vue`](apps/operator-web/src/views/PartnerManagement.vue)
- [`apps/operator-web/src/views/NotificationManagement.vue`](apps/operator-web/src/views/NotificationManagement.vue)

---

## 四、执行顺序

```
任务 1 (运营端基础架构) 
    → 任务 2 (学生端数据对接)
    → 任务 3 (家长端数据对接)
    → 任务 4 (教师端数据对接)
    → 任务 5 (学生端游戏引擎扩展)
    → 任务 6 (运营端管理功能增强)
```

总预计工时: 约 2-3 天（单人开发）