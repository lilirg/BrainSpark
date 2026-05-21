
# BrainSpark Figma 设计系统规范

> 版本: 1.0.0 | 最后更新: 2026-05-21
> 适用工具: Figma (Design + Dev Mode)

---

## 目录

1. [文件结构](#文件结构)
2. [样式设置（Styles）](#样式设置styles)
3. [文本设置（Text Styles）](#文本设置text-styles)
4. [组件库（Components）](#组件库components)
5. [页面模板（Templates）](#页面模板templates)
6. [设计规范](#设计规范)
7. [交接说明](#交接说明)

---

## 文件结构

### 文件夹树状结构

```
BrainSpark Design System
├── 📄 00 Cover / README
├── 📄 01 Getting Started
│   ├── 设计原则
│   ├── 色彩系统
│   └── 字体系统
├── 📄 02 Student Web（学生端）
│   ├── Components / Student
│   ├── Templates / 登录页
│   ├── Templates / 任务中心
│   ├── Templates / 舒尔特方格游戏
│   ├── Templates / 结果与奖励
│   └── Themes / 太空 海洋 森林 科学 经典
├── 📄 03 Parent Web（家长端）
│   ├── Components / Parent
│   ├── Templates / 仪表板
│   ├── Templates / 报告详情
│   ├── Templates / 成长追踪
│   └── Templates / 报告对比
├── 📄 04 Teacher Web（教师端）
│   ├── Components / Teacher
│   ├── Templates / 工作台
│   ├── Templates / 用户管理
│   ├── Templates / 报告协助
│   └── Templates / 消息中心
├── 📄 05 Shared Components（共享组件）
│   ├── Buttons / Primary  Secondary  Text  Icon
│   ├── Cards / Base  Stat  Report  Empty State
│   ├── Inputs / Input  Select  DatePicker
│   ├── Navigation / Sidebar  Navbar  Tabs  Breadcrumb
│   ├── Feedback / Toast  Modal  Drawer  Skeleton
│   ├── Data Viz / Radar  Line Chart  Bar Chart  Pie
│   └── Loading / Spinner  ProgressBar  Steps
├── 📄 06 Assets（资源）
│   ├── Icons / Brand  Navigation  Action  Feedback
│   ├── Illustrations / Empty States  Success  Error
│   ├── Logos / BrainSpark Logo Mark  Logotype
│   └── SFX Preview /（参考图）
└── 📄 99 Archive /（历史版本）
```

---

## 样式设置（Styles）

### 颜色样式（Color Styles）

#### 品牌色

| 样式名 | 类型 | 色值 | 应用 |
|--------|------|------|------|
| `Brand/Primary` | Solid | `#4F6EF7` | 主按钮、链接、激活态 |
| `Brand/Secondary` | Solid | `#FF6B9D` | 强调色、互动反馈 |
| `Brand/Spirit/Orange` | Solid | `#FF8A35` | 奖励、徽章 |
| `Brand/Spirit/Green` | Solid | `#34D399` | 成功、进度完成 |
| `Brand/Spirit/Purple` | Solid | `#8B5CF6` | AI 建议、分析模块 |
| `Brand/Spirit/Blue` | Solid | `#38BDF8` | 安全提示、教育建议 |

#### 语义色（全局共享）

| 样式名 | 类型 | 色值 | 应用 |
|--------|------|------|------|
| `Semantic/Success` | Solid | `#34D399` | 成功提示、绿色评级 |
| `Semantic/Warning` | Solid | `#F59E0B` | 警告提示、黄色评级 |
| `Semantic/Danger` | Solid | `#F87171` | 错误提示、红色评级 |
| `Semantic/Info` | Solid | `#38BDF8` | 信息提示、蓝色标识 |

#### 学生端主题色

| 样式名 | 类型 | 色值 | 应用 |
|--------|------|------|------|
| `Student/Space/Text` | Solid | `#FFFFFF` | 文字 |
| `Student/Space/Nav` | Solid | `#1A1A2E` | 深空背景 |
| `Student/Space/Cell` | Solid | `#FF6B35` | 能量橙 → 方格 |
| `Student/Space/Feedback` | Solid | `#00D2FF` | 量子青 → 点击反馈 |
| `Student/Space/Glow` | Solid | `#FFD700` | 荣耀金 → 高亮边框 |
| `Student/Space/Reward` | Solid | `#8B5CF6` | 星云紫 → 奖励动画 |

| 样式名 | 类型 | 色值 | 应用 |
|--------|------|------|------|
| `Student/Ocean/Nav` | Solid | `#0C1929` | 深海背景 |
| `Student/Ocean/Cell` | Solid | `#06B6D4` | 海洋青 → 水母/气泡 |
| `Student/Ocean/Feedback` | Solid | `#FF6B35` | 珊瑚橙 → 海星 |
| `Student/Ocean/Text` | Solid | `#FFFFFF` | 文字 |

| 样式名 | 类型 | 色值 | 应用 |
|--------|------|------|------|
| `Student/Forest/Nav` | Solid | `#0B2B1A` | 森林深绿背景 |
| `Student/Forest/Cell` | Solid | `#10B981` | 绿叶青 → 树叶/草地 |
| `Student/Forest/Feedback` | Solid | `#EF4444` | 蘑菇红 → 装饰 |
| `Student/Forest/Text` | Solid | `#E8FFEF` | 文字 |

| 样式名 | 类型 | 色值 | 应用 |
|--------|------|------|------|
| `Student/Science/Nav` | Solid | `#0F111A` | 深空背景 |
| `Student/Science/Cell` | Solid | `#8B5CF6` | 实验紫 → 器材 |
| `Student/Science/Feedback` | Solid | `#38BDF8` | 科技蓝 → 数据流 |
| `Student/Science/Reward` | Solid | `#A3E635` | 荧光绿 → 成功 |
| `Student/Science/Text` | Solid | `#E0E7FF` | 文字 |

| 样式名 | 类型 | 色值 | 应用 |
|--------|------|------|------|
| `Student/Classic/Nav` | Solid | `#1E293B` | 深蓝灰背景 |
| `Student/Classic/Cell` | Solid | `#4F6EF7` | 品牌蓝 → 方格 |
| `Student/Classic/Feedback` | Solid | `#60A5FA` | 亮蓝 → 反馈 |
| `Student/Classic/Text` | Solid | `#F1F5F9` | 文字 |

#### 家长/员工中性色

| 样式名 | 类型 | 色值 | 应用 |
|--------|------|------|------|
| `Neutral/100` | Solid | `#F5F7FA` | 浅灰背景 |
| `Neutral/200` | Solid | `#E5E6EB` | 边框、分隔线 |
| `Neutral/300` | Solid | `#B0B8C4` | 禁用态 |
| `Neutral/400` | Solid | `#8B96AB` | 占位符 |
| `Neutral/500` | Solid | `#636B83` | 次文本 |
| `Neutral/700` | Solid | `#3D4556` | 标题 H2-H3 |
| `Neutral/900` | Solid | `#1D2029` | 主文本 |
| `Neutral/Black` | Solid | `#1A1D26` | Logo 文字 |

#### 暗色模式映射

| 样式名 | 类型 | 亮色值 | 暗色值 | 应用 |
|--------|------|--------|--------|------|
| `Theme/Background` | Solid | `#F5F7FA` | `#0F1419` | 页面背景 |
| `Theme/Card` | Solid | `#FFFFFF` | `#1D232B` | 卡片背景 |
| `Theme/Surface` | Solid | `#FFFFFF` | `#1A1F2E` | 侧边栏/面板 |
| `Theme/Bordered` | Solid | `#E5E6EB` | `#2D3748` | 分隔线 |

---

### 渐变色样式（Gradient Styles）

| 样式名 | 类型 | 色值 | 方向 | 应用 |
|--------|------|------|------|------|
| `Gradient/Primary` | Linear | `#4F6EF7` → `#6C5CE7` | 135° | 评分卡、主按钮 hover |
| `Gradient/Student/Gold` | Linear | `#FFD700` → `#FF8A35` | 135° | 奖励动画、徽章 |
| `Gradient/Student/Ocean` | Radial | `#06B6D4` → `#1A1A2E` | center | 海洋主题背景 |
| `Gradient/Student/Forest` | Linear | `#10B981` → `#0B2B1A` | 90° | 森林主题背景 |

---

### 阴影样式（Effect Styles）

| 样式名 | 类型 | 参数 | 应用 |
|--------|------|------|------|
| `Shadow/None` | Drop Shadow | 无 | 卡片静止态 |
| `Shadow/Sm` | Drop Shadow | `0 1px 3px rgba(0,0,0,0.08)` | 输入框 |
| `Shadow/Md` | Drop Shadow | `0 4px 12px rgba(0,0,0,0.1)` | 下拉菜单 |
| `Shadow/Lg` | Drop Shadow | `0 8px 24px rgba(0,0,0,0.12)` | 弹窗 |
| `Shadow/Xl` | Drop Shadow | `0 12px 40px rgba(0,0,0,0.16)` | 全屏抽屉 |
| `Shadow/Glow` | Inner Glow | `0 0 8px rgba(255,215,0,0.4)` 偏移 (0,0) | 学生端高亮 |
| `Shadow/Glow/Feedback` | Inner Glow | `0 0 12px rgba(0,210,255,0.6)` 偏移 (0,0) | 学生端点击反馈 |

---

### 圆角样式（Layer Styles / Border Radii）

| 样式名 | 参数 | 应用 |
|--------|------|------|
| `Radius/None` | `0` | 特殊装饰 |
| `Radius/Sm` | `4px` | 输入框、标签 |
| `Radius/Md` | `8px` | 按钮、列表项 |
| `Radius/Lg` | `12px` | 卡片、弹窗 |
| `Radius/Xl` | `20px` | 学生端方格、徽章 |
| `Radius/Full` | `9999px` | 胶囊按钮、标签 |

---

## 文本设置（Text Styles）

### 学生端文本样式（适龄分级）

#### 6-8 岁组

| 样式名 | 字体 | 字号 | 字重 | 行高 | 应用场景 |
|--------|------|------|------|------|----------|
| `Student/H1/Small` | PingFang SC | `36px` | SemiBold | `1.4` | 引导页小标题 |
| `Student/H1` | PingFang SC | `48px` | SemiBold | `1.2` | 引导页大标题 |
| `Student/CellNum` | SF Pro / Arial | `28px` | Bold | `1` | 方格内数字 |
| `Student/BodyLg` | PingFang SC | `22px` | Regular | `1.5` | 说明文字 |
| `Student/BtnLg` | PingFang SC | `18px` | Medium | `1` | 大按钮 |

#### 9-11 岁组

| 样式名 | 字体 | 字号 | 字重 | 行高 | 应用场景 |
|--------|------|------|------|------|----------|
| `Student/H1/Md` | PingFang SC | `40px` | SemiBold | `1.3` | 引导标题 |
| `Student/CellNum/Md` | SF Pro / Arial | `24px` | Bold | `1` | 方格数字 |
| `Student/BodyMd` | PingFang SC | `20px` | Regular | `1.5` | 说明文字 |
| `Student/BtnMd` | PingFang SC | `16px` | Medium | `1` | 按钮 |

#### 12+ 岁组

| 样式名 | 字体 | 字号 | 字重 | 行高 | 应用场景 |
|--------|------|------|------|------|----------|
| `Student/H1/Lg` | PingFang SC | `32px` | SemiBold | `1.3` | 引导标题 |
| `Student/CellNum/Lg` | SF Pro / Arial | `20px` | Bold | `1` | 方格数字 |
| `Student/BodyLg` | PingFang SC | `18px` | Regular | `1.5` | 说明文字 |
| `Student/Btn` | PingFang SC | `15px` | Medium | `1` | 按钮 |

---

### 家长/教师端文本样式

| 样式名 | 字号 | 行高 | 字重 | 字间距 | 应用场景 |
|--------|------|------|------|--------|----------|
| `Text/H1` | `28px` | `1.4` | SemiBold | `-0.5px` | 页面主标题 |
| `Text/H2` | `22px` | `1.4` | SemiBold | `-0.3px` | 板块标题 |
| `Text/H3` | `18px` | `1.5` | SemiBold | `0` | 子标题 |
| `Text/H4` | `16px` | `1.5` | Medium | `0` | 卡片标题 |
| `Text/Body` | `14px` | `1.57` | Regular | `0` | 正文 |
| `Text/Small` | `12px` | `1.5` | Regular | `0` | 辅助说明 |
| `Text/Button` | `14px` | `1` | Medium | `0` | 按钮 |
| `Text/Caption` | `12px` | `1.5` | Regular | `0` | 备注、标签 |
| `Text/Code` | `13px` | `1.6` | Monospace | `-0.5px` | 代码、ID |

---

## 组件库（Components）

### 按钮（Buttons）

| 组件名 | 变体 | 尺寸 | 填充 | 边框 | 文本颜色 | 图标 |
|--------|------|------|------|------|----------|------|
| `Button/Primary` | Default | H: 40px | `#4F6EF7` | `#4F6EF7` | `#FFFFFF` | 可选 |
| | Hover | H: 40px | `#4357E8` | `#4357E8` | `#FFFFFF` | 可选 |
| | Active | H: 40px | `#3A4CD6` | `#3A4CD6` | `#FFFFFF` | 可选 |
| | Disabled | H: 40px | `#E5E6EB` | `#E5E6EB` | `#B0B8C4` | - |
| `Button/Secondary` | Default | H: 40px | `Transparent` | `#4F6EF7` | `#4F6EF7` | 可选 |
| | Hover | H: 40px | `rgba(79,110,247,0.08)` | `#4F6EF7` | `#4F6EF7` | 可选 |
| `Button/Text` | Default | H: 32px | `Transparent` | 无 | `#4F6EF7` | 可选 |
| `Button/Icon` | Default | 40×40px | `Transparent` | 无 | `#3D4556` | - |

**学生端按钮：**
| 组件名 | H | 填充 | 圆角 | 文本 |
|--------|---|------|------|------|
| `Student/Btn/Sm` | 56px | `#FF6B35` | 28px (胶囊) | 18px SemiBold 白 |
| `Student/Btn/Md` | 64px | `#FF6B35` | 32px (胶囊) | 22px SemiBold 白 |
| `Student/Btn/Lg` | 72px | `#FF6B35` | 36px (胶囊) | 26px Bold 白 |

### 输入框（Inputs）

| 组件名 | 状态 | H | 填充 | 边框 | 圆角 | 提示 |
|--------|------|---|------|------|------|------|
| `Input/Default` | Normal | 40px | `#FFFFFF` | `#E5E6EB` | 8px | 12px 灰色 |
| | Focus | 40px | `#FFFFFF` | `#4F6EF7` | 8px | - |
| | Error | 40px | `#FFFFFF` | `#F87171` | 8px | 12px 红色 |
| | Disabled | 40px | `#F5F7FA` | `#E5E6EB` | 8px | - |

### 卡片（Cards）

| 组件名 | 填充 | 边框 | 圆角 | 阴影 |
|--------|------|------|------|------|
| `Card/Default` | 24px | `1px #E5E6EB` | 12px | 无 |
| `Card/Stat` | 24px | 无 | 12px | Shadow/Md |
| `Card/Elevated` | 24px | 无 | 12px | Shadow/Lg |
| `Card/Danger` | 24px | `1px #F8717133` | 12px | Shadow/None |

### 标签（Tags / Badges）

| 组件名 | 填充 | 文字 | 边框 | 圆角 |
|--------|------|------|------|------|
| `Tag/Success` | `#34D39920` | `#34D399` | 无 | 9999px |
| `Tag/Warning` | `#F59E0B20` | `#F59E0B` | 无 | 9999px |
| `Tag/Danger` | `#F8717120` | `#F87171` | 无 | 9999px |
| `Tag/Info` | `#38BDF820` | `#38BDF8` | 无 | 9999px |
| `Tag/Neutral` | `#E5E6EB` | `#636B83` | 无 | 9999px |
| `Tag/Ghost` | `Transparent` | `#4F6EF7` | `1px #4F6EF733` | 9999px |

### 空状态（Empty States）

| 组件名 | 插画 | 标题 | 说明 | 按钮 |
|--------|------|------|------|------|
| `Empty/Default` | 120×120 | 16px Medium | 14px Regular | Primary 1个 |
| `Empty/Report` | 160×120 | 18px SemiBold | 14px Secondary | Primary + Secondary |

### 加载态（Loading）

| 组件名 | 形态 | 尺寸 | 色值 | 背景 |
|--------|------|------|------|------|
| `Loading/Spinner` | 环形旋转 | 24×24, 32×32, 48×48 | `#4F6EF7` | - |
| `Loading/Skeleton` | 灰块闪烁 | 可变 | 无 | `#E5E6EB` / `#F5F7FA` |
| `Loading/Bar` | 进度条 | H: 4px | `#4F6EF7` | `#E5E6EB` |
| `Loading/Steps` | 步骤指示 | 40×40 圆圈 | 当前: `#4F6EF7` | - |

### 反馈（Feedback）

| 组件名 | 类型 | H | 填充 | 图标 | 文字 | 圆角 |
|--------|------|---|------|------|------|------|
| `Toast/Success` | 底部居中 | 48px | `#1A1D26` | ✓ 白 | 14px 白 | 8px |
| `Toast/Error` | 底部居中 | 48px | `#1A1D26` | ✕ 白 | 14px 白 | 8px |
| `Toast/Info` | 底部居中 | 48px | `#1A1D26` | ⓘ 白 | 14px 白 | 8px |
| `Alert/Success` | 行内 | Auto | `#34D39915` | - | 14px #1A1D26 | 8px |
| `Alert/Error` | 行内 | Auto | `#F8717115` | - | 14px #1A1D26 | 8px |
| `Alert/Warning` | 行内 | Auto | `#F59E0B15` | - | 14px #1A1D26 | 8px |

### 导航（Navigation）

| 组件名 | 类型 | H | 填充 | 边框 | 圆角 |
|--------|------|---|------|------|------|
| `Nav/Sidebar/Default` | 左侧栏 | Full | `#FFFFFF` | 右 `1px #E5E6EB` | 无 |
| `Nav/Sidebar/Active` | 左侧栏 | Full | `#E8EDFF` | - | 无 |
| `Nav/Tab/Default` | Tab 栏 | 44px | - | 底 `2px Transparent` | 无 |
| `Nav/Tab/Active` | Tab 栏 | 44px | - | 底 `2px #4F6EF7` | 无 |
| `Nav/Pagination` | 分页 | 40px/项 | - | 无 | 8px |

### 数据可视化（Data Viz）- ECharts 映射

| 图表类型 | Figma 组件 | 关键属性 |
|----------|-----------|----------|
| 雷达图 | `Chart/Radar` | 填充 `#4F6EF730`, 边界 `#4F6EF7` 2px, 刻度 `#E5E6EB` 1px |
| 折线图 | `Chart/Line` | 主色 `#4F6EF7`, 填充 `#4F6EF720`, 常模线 `#E5E6EB` 2px dashed |
| 柱状图 | `Chart/Bar` | 对比柱 `#4F6EF7` / `#A8B8D8` 间距 40%, 圆角 4px |
| 饼图 | `Chart/Pie` | 色板 `#4F6EF7, #FF6B9D, #34D399, #F59E0B, #8B5CF6, #38BDF8` |

---

## 页面模板（Templates）

### 学生端模板（Student Web）

#### 登录页 / Template: Student Login

```
┌─────────────────────────────────────────┐
│                                         │
│         BrainSpark Logo                 │
│         (120×40)                        │
│                                         │
│     ┌─────────────────────────┐         │
│     │                        │         │
│     │    🌟 太空探险主题      │         │
│     │    背景图 / Illustration│         │
│     │                        │         │
│     └─────────────────────────┘         │
│                                         │
│   ┌───────────────────────────┐         │
│   │      [请输入学生码]       │         │
│   └───────────────────────────┘         │
│                                         │
│          ┌──────────────────┐           │
│          │     开始游戏 🚀   │           │
│          └──────────────────┘           │
│                                         │
│   ┌────┐  ┌────┐                         │
│   │音效 │  │设置│                         │
│   └────┘  └────┘                         │
└─────────────────────────────────────────┘
```

| 区域 | 组件 | 尺寸 | 间距 |
|------|------|------|------|
| Logo | Brand/Logotype | 120×40 | 顶部 32px |
| 中心区域 | Illustration | 320×280 | 上下 120px |
| 输入框 | Input/Default | 280×48 | 中间 24px |
| 主按钮 | Student/Btn/Md | 280×64 | 输入框 16px |

#### 游戏页 / Template: Schulte Grid Game

```
┌─────────────────────────────────────────┐
│  ⏱ 03:45              🔊 静音           │ ← H: 56px
├─────────────────────────────────────────┤
│                                         │
│         ┌───┬───┬───┬───┬───┐           │
│         │ 16│  3│ 28│  7│ 11│           │ ← 64px 间距
│         ├───┼───┼───┼───┼───┤           │
│         │  9│ 22│  5│ 18│  1│           │ 48px 间距
│         ├───┼───┼───┼───┼───┤           │
│         │ ...                          │
│         └───┴───┴───┴───┴───┘           │
│                                         │
│         ⬛ ⬛ ⬛ ⬛ ⬛ ← 星星指示器       │
│                                         │
│     ┌────────┐   ←─ 进度条 H:12px      │
│     ████████░░                           │
└─────────────────────────────────────────┘
```

| 规则 | 约束 |
|------|------|
| 禁止侧边栏 | ❌ 无导航、无菜单 |
| 禁止弹窗 | ❌ 中断会销毁沉浸式体验 |
| 禁止键盘输入 | ❌ 仅 PointerEvent 点击/触摸 |
| 底部按钮最多 | 4 个以内（开始/重置/音效/暂停） |

---

### 家长端模板（Parent Web）

#### 报告详情页 / Template: Report Detail

```
┌──────────────────────────────────────────────────────────┐
│  BrainSpark 家长端                            张先生 🏠 ▼│
├────────────────┬─────────────────────────────────────────┤
│ 🏠 我的家庭     │  📄 报告中心   │                       │
│ 📄 报告中心  ●  │                                                 │
│ 📈 成长追踪    │  ┌───────────────────────────────┐     │
│ 📋 训练计划     │  │ 综合能力评分   │  📅 2026-05 │     │
│ 👑 会员订阅    │  │                       │  ▼      │     │
│ ⚙️ 设置        │  │       87          │                       │
│                │  │      良  好       │  ┌──────┐         │
│                │  │  ┌────────────┐   │  │  ⭕  │    👁   │     │
│                │  │  │ 雷达图预览  │   │  └──────┘         │
│                │  │  └────────────┘   │  ┌─────────────┐ │
│                │  │                   │  │ 下载 PDF  📥│ │
│                │  │  ───────────────  │  └─────────────┘ │
│                │  │  AI 教育建议       │  ┌─────────────┐ │
│                │  │  ✨ 您在「工作记忆」│  │  📊 对比分析 │ │
│                │  │    方面表现良好...  │  └─────────────┘ │
│                │  └───────────────────────────────┘     │
│                │  ┌───────────────────────────────┐     │
│                │  │  📈 成长趋势                  │     │
│                │  │  [ECharts Line Chart 16:9]    │     │
│                │  └───────────────────────────────┘     │
└────────────────┴─────────────────────────────────────────┘
```

| 规则 | 约束 |
|------|------|
| 下载报告按钮 | 固定位置，点击即触发，无需确认 |
| 对比入口 | 标签切换，不需跳转新页面 |
| Banner 通知 | ❌ 不使用全局 Banner，用 Toast/小红点 |
| 表单输入 | ❌ 非必填场景不展示输入框 |

---

### 教师端模板（Teacher Web）

#### 工作台 / Template: Dashboard

```
┌────────────────────────────────────────────────────┐
│ BrainSpark 运营平台                       🔍 🔔 🔑│
├──────────┬─────────────────────────────────────────┤
│ 🏠 工作台 │   今日工作概览                           │
│ 👥 用户管理│  ┌────────────────────────────────┐   │
│ 📝 测评服务│  │ 用户数 待处理 新注册 待跟进    │   │
│ 📄 报告协助│  │ 1,234   12    28     7         │   │
│ 💬 消息中心│  └────────────────────────────────┘   │
│ ⚙️ 设置    │                                         │
└──────────┴─────────────────────────────────────────┘
```

---

## 设计规范

### 间距系统

Figma 中使用 **8pt 网格系统**，变量映射：

| 变量名 | Figma 值 | 用途 |
|--------|----------|------|
| `space/025` | `4` | 极小（输入框内边距） |
| `space/050` | `8` | 小（标签间距） |
| `space/075` | `12` | 中小（表单元素间距） |
| `space/100` | `16` | 标准（默认间距） |
| `space/150` | `24` | 中等（卡片内边距） |
| `space/200` | `32` | 大（板块间距） |
| `space/300` | `48` | 超大（页面边距） |
| `space/400` | `64` | 超大（大间距） |

### 断点系统

| 断点名 | 宽度 | 应用 |
|--------|------|------|
| `breakpoint/sm` | `640px` | 家长端移动端横屏 |
| `breakpoint/md` | `1024px` | 平板、教师端 |
| `breakpoint/lg` | `1280px` | 桌面标准 |
| `breakpoint/xl` | `1536px` | 大屏桌面 |
| `breakpoint/2xl` | `1920px` | 超宽屏 |

### Auto Layout 规范

| 组件 | Main Axis | Cross Axis | 间距模式 |
|------|-----------|------------|----------|
| 按钮（含图标） | 水平居中 | 居中 | Item Spacing: 8px |
| 导航项 | 垂直居中 | 居中 | Auto Horizo

[Response interrupted by user request]