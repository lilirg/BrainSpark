# BrainSpark API 设计文档

> 版本: 1.0.0 | 最后更新: 2026-05-19

## 目录

1. [概述](#概述)
2. [通用规范](#通用规范)
3. [认证与授权](#认证与授权)
4. [用户管理 API](#用户管理-api)
5. [班级与档案管理 API](#班级与档案管理-api)
6. [测评任务 API](#测评任务-api)
7. [行为事件采集 API](#行为事件采集-api)
8. [AI 分析与报告 API](#ai-分析与报告-api)
9. [家长端 API](#家长端-api)
10. [运营管理 API](#运营管理-api)
11. [运维监控 API](#运维监控-api)
12. [WebSocket 实时通信](#websocket-实时通信)
13. [错误处理](#错误处理)
14. [OpenAPI 规范](#openapi-规范)

---

## 概述

BrainSpark 采用微服务架构，API 按服务域划分：

| 服务 | 端口 | 路由前缀 | 说明 |
|------|------|----------|------|
| 业务后端 | 8080 | `/api/v1` | 用户、班级、测评任务、报告 CRUD |
| 高并发网关 | 8081 | `/api/v1` | 游戏结果实时采集、WebSocket |
| AI 服务 | 8001 | `/ai/v1` | 认知分析、报告生成、RAG 检索 |
| 运营管理 | 8080 | `/api/v1/admin` | 内容管理、数据统计、系统配置 |

---

## 通用规范

### 请求格式

- 路径: RESTful 风格
- 请求体: `application/json`
- 认证: `Authorization: Bearer <token>`

### 统一响应格式

```json
{
  "code": 200,
  "data": {},
  "message": "ok",
  "traceId": "req-xxxxx"
}
```

### 分页参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `page` | int | 页码，从 1 开始，默认 1 |
| `size` | int | 每页数量，默认 20，最大 100 |

### 统一分页响应

```json
{
  "code": 200,
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "size": 20
  }
}
```

---

## 认证与授权

### 用户角色

| 角色 | 说明 | 权限范围 |
|------|------|----------|
| `ADMIN` | 系统管理员 | 全部权限 |
| `TEACHER` | 教师 | 班级管理、学生档案、报告查看 |
| `STUDENT` | 学生 | 测评任务、个人报告 |
| `PARENT` | 家长 | 关联子女的报告查看、设置 |

### 认证流程

```
登录 ──POST /api/v1/auth/login──▶ 返回 JWT ──后续请求带 Authorization Header──▶ 网关验证
```

### API 端点

#### 登录

```
POST /api/v1/auth/login
```

**请求体**

```json
{
  "username": "teacher01",
  "password": "********"
}
```

**响应**

```json
{
  "code": 200,
  "data": {
    "accessToken": "eyJhbGc...",
    "refreshToken": "eyJhbGc...",
    "expiresIn": 7200,
    "role": "TEACHER"
  }
}
```

#### 刷新 Token

```
POST /api/v1/auth/refresh
```

**请求体**

```json
{
  "refreshToken": "eyJhbGc..."
}
```

#### 登出

```
POST /api/v1/auth/logout
```

请求头需携带有效 `Authorization`，服务端注销 Token。

#### 获取当前用户信息

```
GET /api/v1/auth/me
```

响应 `data` 返回当前用户的 [`UserInfo`](packages/shared-types/src/user.ts:1) 对象（不含密码字段）。

---

## 用户管理 API

基础路径: `/api/v1/users`

### 端点列表

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/users` | 用户列表（分页） | `ADMIN`, `TEACHER` |
| `GET` | `/users/{id}` | 获取用户详情 | `ADMIN`, 本人 |
| `POST` | `/users` | 创建用户 | `ADMIN`, `TEACHER` |
| `PUT` | `/users/{id}` | 更新用户 | `ADMIN`, 本人 |
| `DELETE` | `/users/{id}` | 删除用户 | `ADMIN` |

### 创建用户请求体

```json
{
  "username": "student001",
  "password": "********",
  "role": "STUDENT",
  "realName": "小明",
  "age": 10,
  "grade": "四年级",
  "avatar": "https://..."
}
```

> **注意**: 创建学生用户时，教师需关联一个父账号 [`Parent`](apps/backend-business/src/main/java/com/brainspark/entity/User.java:39) 以实现监护关系。

---

## 班级与档案管理 API

### 班级管理

基础路径: `/api/v1/classes`

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/classes` | 班级列表（分页） | `TEACHER` |
| `POST` | `/classes` | 创建班级 | `TEACHER` |
| `GET` | `/classes/{id}` | 班级详情 | `TEACHER` |
| `PUT` | `/classes/{id}` | 更新班级 | `TEACHER` |
| `DELETE` | `/classes/{id}` | 删除班级 | `TEACHER` |
| `POST` | `/classes/{id}/members` | 添加学生 | `TEACHER` |
| `DELETE` | `/classes/{id}/members/{studentId}` | 移除学生 | `TEACHER` |

#### 创建班级请求体

```json
{
  "name": "三年级二班",
  "grade": 3,
  "teacherId": "uuid-xxx",
  "description": "2026春季学期"
}
```

### 学生档案

基础路径: `/api/v1/students`

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/students` | 学生列表（按班级筛选） | `TEACHER` |
| `GET` | `/students/{id}` | 学生档案详情 | `TEACHER`, `PARENT`, 本人 |
| `PUT` | `/students/{id}/profile` | 更新档案 | `TEACHER`, `PARENT` |
| `GET` | `/students/{id}/growth` | 成长趋势数据 | `TEACHER`, `PARENT`, 本人 |

#### 成长趋势响应

```json
{
  "code": 200,
  "data": {
    "userId": "uuid-xxx",
    "records": [
      {
        "date": "2026-05-01",
        "radar": {
          "attention": 85,
          "memory": 72,
          "logic": 90,
          "language": 68,
          "spatial": 78,
          "executiveFunction": 82
        }
      }
    ]
  }
}
```

---

## 测评任务 API

基础路径: `/api/v1/assessments`

### 任务管理

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/assessments/tasks` | 测评任务列表 | `TEACHER` |
| `POST` | `/assessments/tasks` | 创建任务 | `TEACHER` |
| `GET` | `/assessments/tasks/{id}` | 任务详情 | `TEACHER` |
| `PUT` | `/assessments/tasks/{id}` | 更新任务 | `TEACHER` |
| `DELETE` | `/assessments/tasks/{id}` | 删除任务 | `TEACHER` |
| `GET` | `/assessments/tasks/today` | 今日待测任务 | `STUDENT` |
| `GET` | `/assessments/tasks/assigned` | 已分配给当前学生的任务 | `STUDENT` |

#### 任务类型

基于 [`AssessmentType`](packages/shared-types/src/assessment.ts:1) 枚举:

- `SCHULTE_GRID` - 舒尔特方格（视觉注意力）
- `NUMBER_SPAN` - 数字广度（工作记忆）
- `PATTERN_RECOGNITION` - 图形推理（逻辑思维）

#### 创建任务请求体

```json
{
  "name": "舒尔特方格-基础版",
  "type": "SCHULTE_GRID",
  "description": "标准5x5网格，限时60秒",
  "difficulty": 1,
  "duration": 60,
  "config": {
    "gridSize": 5,
    "timeLimit": 60,
    "theme": "space"
  },
  "assignedClassIds": ["class-uuid-1"]
}
```

### 测评结果

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/assessments/results` | 结果列表（分页） | `TEACHER` |
| `GET` | `/assessments/results/{id}` | 结果详情 | `TEACHER`, `PARENT` |
| `POST` | `/assessments/results` | 提交测评结果 | `STUDENT`（通过网关转发） |

#### 测评结果请求/响应

基于 [`AssessmentResult`](packages/shared-types/src/assessment.ts:18) 接口:

```json
{
  "id": "result-uuid",
  "userId": "student-uuid",
  "taskId": "task-uuid",
  "taskType": "SCHULTE_GRID",
  "score": 85,
  "percentile": 92,
  "accuracy": 0.96,
  "avgReactionTime": 1.2,
  "maxReactionTime": 3.5,
  "minReactionTime": 0.6,
  "completedAt": "2026-05-19T08:30:00Z"
}
```

---

## 行为事件采集 API

> **注意**: 高频事件（点击、指针移动）通过 **网关 `/api/v1/events`** 提交，由 Go 网关直接写入 ClickHouse 或 MongoDB，以支持高并发采集。

基础路径: `/api/v1/events` (由 Go 网关处理)

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `POST` | `/events/batch` | 批量提交行为事件 | 所有角色 |
| `POST` | `/events/ws` | WebSocket 事件流 | `STUDENT` |

### 批量提交

```
POST /api/v1/events/batch
```

**请求体**

```json
{
  "studentId": "student-uuid",
  "assessmentId": "assessment-uuid",
  "sessionId": "session-uuid",
  "events": [
    {
      "timestamp": 1716105600000,
      "eventType": "click",
      "data": {
        "x": 150,
        "y": 200,
        "targetNumber": 5,
        "reactionTime": 1.2
      }
    },
    {
      "timestamp": 1716105601200,
      "eventType": "keypress",
      "data": {
        "key": "5",
        "reactionTime": 0.8
      }
    }
  ]
}
```

### 事件类型

基于 [`BehaviorEventType`](packages/shared-types/src/assessment.ts:32):

| 类型 | 说明 |
|------|------|
| `CLICK` | 点击事件 |
| `HOVER` | 悬停事件 |
| `KEY_PRESS` | 键盘事件 |
| `ASSESSMENT_START` | 测评开始 |
| `ASSESSMENT_END` | 测评结束 |
| `ASSESSMENT_ABORT` | 测评中断 |

---

## AI 分析与报告 API

### 评估分析

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `POST` | `/ai/v1/assessments/analyze` | 分析测评数据 | `TEACHER` |

**请求体**

基于 [`AssessmentRequest`](apps/ai-service/app/schemas/assessment.py:13):

```json
{
  "student_id": "student-uuid",
  "events": [
    {
      "event_type": "click",
      "dimension": "attention",
      "score": 85.5,
      "timestamp": "2026-05-19T08:30:00Z"
    }
  ]
}
```

**响应**

基于 [`AssessmentResponse`](apps/ai-service/app/schemas/assessment.py:24):

```json
{
  "code": 200,
  "data": {
    "student_id": "student-uuid",
    "dimensions": [
      {"dimension": "attention", "score": 85.5, "level": "优秀"},
      {"dimension": "memory", "score": 72.3, "level": "良好"}
    ],
    "overall_score": 82.4,
    "suggestions": ["建议加强视觉注意力训练"]
  }
}
```

### 报告生成

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `POST` | `/ai/v1/reports/generate` | 生成AI报告 | `TEACHER` |

**请求体**

基于 [`ReportRequest`](apps/ai-service/app/schemas/report.py:6):

```json
{
  "student_id": "student-uuid",
  "assessment": {
    "results": [...],
    "radar": {
      "attention": 85,
      "memory": 72,
      "logic": 90,
      "language": 68,
      "spatial": 78,
      "executiveFunction": 82
    }
  },
  "context": "学生年龄10岁，年级四年级"
}
```

**响应**

基于 [`ReportResponse`](apps/ai-service/app/schemas/report.py:12) 及 [`AIReport`](packages/shared-types/src/report.ts:10):

```json
{
  "code": 200,
  "data": {
    "student_id": "student-uuid",
    "report": {
      "id": "report-uuid",
      "capabilityRadar": { ... },
      "summary": "该生在逻辑思维能力方面表现突出...",
      "strengths": ["逻辑思维", "注意力集中"],
      "weaknesses": ["语言处理速度"],
      "recommendations": ["建议增加图形推理训练"],
      "trainingPlan": [
        {
          "title": "每日舒尔特方格训练",
          "type": "attention",
          "duration": 10,
          "frequency": "每日",
          "difficulty": 1
        }
      ],
      "generatedAt": "2026-05-19T09:00:00Z",
      "modelVersion": "1.0"
    }
  }
}
```

### 报告管理

基础路径: `/api/v1/reports`

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/reports` | 报告列表（分页） | `TEACHER`, `PARENT` |
| `GET` | `/reports/{id}` | 报告详情 | `TEACHER`, `PARENT` |
| `POST` | `/reports/{id}/regenerate` | 重新生成报告 | `TEACHER` |
| `GET` | `/reports/{id}/download` | 下载报告（PDF） | `PARENT` |

### 知识索引

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `POST` | `/ai/v1/knowledge/index` | 索引知识库文档 | `ADMIN` |

---

## 家长端 API

### 子女管理

基础路径: `/api/v1/parent/children`

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/parent/children` | 关联子女列表 | `PARENT` |
| `POST` | `/parent/children/bind` | 绑定子女 | `PARENT` |
| `DELETE` | `/parent/children/{childId}` | 解除绑定 | `PARENT` |

### 家长视图

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/parent/dashboard/{childId}` | 子女仪表板数据 | `PARENT` |
| `GET` | `/parent/usage` | 使用时长统计 | `PARENT` |
| `PUT` | `/parent/settings` | 家长设置 | `PARENT` |

---

## 运营管理 API

> **说明**: 运营管理 API 供平台运营人员使用，包括内容管理、数据统计、系统配置、机构合作管理等。
> 角色要求：`ADMIN` 或具有 `OPERATOR` 运营权限。

### 新增角色：OPERATOR（运营）

| 角色 | 说明 | 权限范围 |
|------|------|----------|
| `OPERATOR` | 运营人员 | 内容管理、数据分析、系统配置、审核管理 |

### 内容管理

基础路径: `/api/v1/admin/content`

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/admin/content测评库` | 测评量表列表 | `ADMIN`, `OPERATOR` |
| `POST` | `/admin/content/assessments` | 上架新测评 | `ADMIN`, `OPERATOR` |
| `PUT` | `/admin/content/assessments/{id}` | 更新测评配置 | `ADMIN`, `OPERATOR` |
| `POST` | `/admin/content/assessments/{id}/publish` | 发布测评 | `ADMIN` |
| `POST` | `/admin/content/assessments/{id}/hide` | 下架测评 | `ADMIN` |

#### 测评配置请求体

```json
{
  "name": "舒尔特方格-进阶版",
  "type": "SCHULTE_GRID",
  "difficulty": 2,
  "config": {
    "gridSize": 5,
    "timeLimit": 45,
    "theme": "space",
    "targetNumbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
  },
  "minAge": 6,
  "maxAge": 12,
  "isFree": false,
  "requiresPremium": true
}
```

### 知识库管理

基础路径: `/api/v1/admin/knowledge`

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/admin/knowledge/docs` | 知识库文档列表（分页） | `ADMIN`, `OPERATOR` |
| `POST` | `/admin/knowledge/docs` | 新增知识文档 | `ADMIN`, `OPERATOR` |
| `PUT` | `/admin/knowledge/docs/{id}` | 更新知识文档 | `ADMIN`, `OPERATOR` |
| `DELETE` | `/admin/knowledge/docs/{id}` | 删除知识文档 | `ADMIN` |
| `POST` | `/admin/knowledge/rebuild` | 重新构建向量索引 | `ADMIN` |

### 数据统计

基础路径: `/api/v1/admin/analytics`

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/admin/analytics/dashboard` | 运营仪表板总览 | `ADMIN`, `OPERATOR` |
| `GET` | `/admin/analytics/users` | 用户增长数据 | `ADMIN`, `OPERATOR` |
| `GET` | `/admin/analytics/assessments` | 测评完成统计 | `ADMIN`, `OPERATOR` |
| `GET` | `/admin/analytics/reports` | 报告生成统计 | `ADMIN`, `OPERATOR` |
| `GET` | `/admin/analytics/revenue` | 收入统计（含机构结算） | `ADMIN` |

#### 运营仪表板响应

```json
{
  "code": 200,
  "data": {
    "totalUsers": 12580,
    "activeUsers": {
      "today": 856,
      "week": 3245,
      "month": 8921
    },
    "assessmentsToday": 320,
    "reportsGeneratedToday": 285,
    "revenueToday": 5680,
    "revenueMonth": 186500,
    "topAssessments": [
      {"type": "SCHULTE_GRID", "completions": 15420, "avgScore": 82.5},
      {"type": "NUMBER_SPAN", "completions": 8930, "avgScore": 68.3}
    ],
    "userGrowth7d": [120, 135, 128, 142, 156, 148, 165]
  }
}
```

### 机构合作管理

基础路径: `/api/v1/admin/partners`

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/admin/partners` | 合作机构列表 | `ADMIN`, `OPERATOR` |
| `POST` | `/admin/partners` | 新增合作机构 | `ADMIN` |
| `GET` | `/admin/partners/{id}` | 机构详情 | `ADMIN`, `OPERATOR` |
| `PUT` | `/admin/partners/{id}` | 更新机构信息 | `ADMIN` |
| `GET` | `/admin/partners/{id}/analytics` | 机构数据看板 | `ADMIN`, `OPERATOR` |

#### 新增机构请求体

```json
{
  "name": "阳光教育集团",
  "type": "TRAINING_CENTER",
  "contactPerson": "张经理",
  "contactPhone": "13800138000",
  "maxStudents": 500,
  "priceMultiplier": 0.8,
  "features": ["CLASS_MANAGEMENT", "REPORT_VIEWING"]
}
```

### 审核管理

基础路径: `/api/v1/admin/moderation`

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/admin/moderation/reports` | 报告反馈列表 | `ADMIN`, `OPERATOR` |
| `PUT` | `/admin/moderation/reports/{id}` | 处理反馈 | `ADMIN`, `OPERATOR` |
| `GET` | `/admin/moderation/contents` | 用户生成内容审核 | `ADMIN`, `OPERATOR` |
| `POST` | `/admin/moderation/contents/{id}/approve` | 通过审核 | `ADMIN`, `OPERATOR` |
| `POST` | `/admin/moderation/contents/{id}/reject` | 驳回审核 | `ADMIN`, `OPERATOR` |

### 系统配置

基础路径: `/api/v1/admin/config`

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/admin/config` | 获取所有配置项 | `ADMIN` |
| `PUT` | `/admin/config/{key}` | 更新配置项 | `ADMIN` |
| `POST` | `/admin/config/batch` | 批量更新配置 | `ADMIN` |

#### 配置项示例

```json
{
  "key": "assessment.defaultTimeLimit",
  "value": "60",
  "type": "NUMBER",
  "description": "默认测评时长(秒)",
  "editable": true
}
```

### 通知管理

基础路径: `/api/v1/admin/notifications`

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/admin/notifications` | 通知列表（分页） | `ADMIN`, `OPERATOR` |
| `POST` | `/admin/notifications` | 创建通知 | `ADMIN`, `OPERATOR` |
| `PUT` | `/admin/notifications/{id}` | 更新通知 | `ADMIN` |
| `POST` | `/admin/notifications/{id}/send` | 发送通知 | `ADMIN`, `OPERATOR` |
| `DELETE` | `/admin/notifications/{id}` | 删除通知 | `ADMIN` |

---

## 订单与支付 API

> **说明**: 订单与支付 API 支持 BrainSpark 的商业模式，包括单次报告购买和年度订阅服务。
> 参考商业模式：专业版订阅（¥199/年）、单次深度报告（¥29/次）。

### 商品与套餐

基础路径: `/api/v1/shop`

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/shop/products` | 商品列表（公开发布的商品） | 所有登录用户 |
| `GET` | `/shop/products/{id}` | 商品详情 | 所有登录用户 |
| `GET` | `/shop/packages` | 套餐列表 | 所有登录用户 |
| `GET` | `/shop/redeem` | 优惠券兑换 | 所有登录用户 |

#### 商品/套餐类型

| 类型 | 说明 | 价格示例 |
|------|------|----------|
| `SINGLE_REPORT` | 单次深度 AI 报告 | ¥29 |
| `SUBSCRIPTION_YEARLY` | 专业版年度订阅 | ¥199/年 |
| `SUBSCRIPTION_MONTHLY` | 专业版月度订阅 | ¥29/月 |
| `COUPON` | 优惠券/兑换码 | 折扣面值 |
| `BUNDLE` | 组合套餐（测评+报告+训练） | ¥99 |

#### 商品响应示例

```json
{
  "code": 200,
  "data": {
    "id": "product-uuid",
    "name": "专业版年度订阅",
    "type": "SUBSCRIPTION_YEARLY",
    "price": 19900,
    "originalPrice": 29900,
    "currency": "CNY",
    "features": [
      "全模块测评无限制",
      "深度 AI 认知报告",
      "个性化训练计划",
      "季度能力追踪"
    ],
    "isValid": true,
    "publishAt": "2026-01-01T00:00:00Z"
  }
}
```

### 订单管理

基础路径: `/api/v1/orders`

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `POST` | `/orders` | 创建订单 | 所有登录用户 |
| `GET` | `/orders` | 我的订单列表（分页） | 所有登录用户 |
| `GET` | `/orders/{id}` | 订单详情 | 订单创建者 |
| `POST` | `/orders/{id}/cancel` | 取消订单 | 订单创建者 |
| `GET` | `/orders/{id}/status` | 查询订单状态 | 订单创建者 |

#### 创建订单请求体

```json
{
  "items": [
    {
      "productId": "product-uuid",
      "productName": "专业版年度订阅",
      "quantity": 1,
      "unitPrice": 19900,
      "type": "SUBSCRIPTION_YEARLY"
    }
  ],
  "couponCode": "BRAINSPARK2026",
  "requestId": "unique-request-uuid",
  "redirectUrl": "https://parent.brainspark.com/pay-success"
}
```

**响应**

```json
{
  "code": 200,
  "data": {
    "orderId": "order-uuid",
    "amount": 19900,
    "discount": 0,
    "totalAmount": 19900,
    "expireAt": "2026-05-19T09:30:00Z",
    "payMethods": ["WECHAT_PAY", "ALIPAY"],
    "paymentUrl": "https://pay.brainspark.com/checkout?order_id=...",
    "status": "PENDING"
  }
}
```

#### 订单状态流转

```
CREATED -> PENDING_PAY -> PAID -> COMPLETED
                 |              |
                 |              |---> REFUNDING -> REFUNDED
                 v
              CANCELLED / EXPIRED
```

### 支付回调

> **注意**: 这是第三方支付平台的回调地址，客户端无需调用。

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/payments/wechat/callback` | 微信支付回调 |
| `POST` | `/api/v1/payments/alipay/callback` | 支付宝回调 |
| `POST` | `/api/v1/payments/verify` | 验证支付结果（客户端轮询用） |

#### 验证支付响应

```json
{
  "code": 200,
  "data": {
    "orderId": "order-uuid",
    "status": "PAID",
    "paidAt": "2026-05-19T09:01:00Z",
    "transactionId": "wechat_trans_123456",
    "activatedFeatures": ["SUBSCRIPTION_YEARLY"]
  }
}
```

### 订阅管理

基础路径: `/api/v1/subscription`

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `GET` | `/subscription/status` | 当前订阅状态 | 所有登录用户 |
| `GET` | `/subscription/history` | 订阅历史 | 所有登录用户 |
| `POST` | `/subscription/cancel` | 取消订阅（下周期生效） | 当前订阅者 |
| `POST` | `/subscription/reactivate` | 重新激活订阅 | 已取消未过期的订阅 |
| `GET` | `/subscription/benefits` | 权益清单 | 所有登录用户 |

#### 订阅状态响应

```json
{
  "code": 200,
  "data": {
    "isActive": true,
    "planType": "SUBSCRIPTION_YEARLY",
    "startedAt": "2026-01-15T00:00:00Z",
    "expiresAt": "2027-01-15T00:00:00Z",
    "autoRenew": true,
    "remainingDays": 235,
    "features": [
      {"name": "全模块测评", "unlimited": true},
      {"name": "深度 AI 报告", "unlimited": true},
      {"name": "季度能力追踪", "available": true}
    ]
  }
}
```

### 发票管理

基础路径: `/api/v1/invoices`

| 方法 | 路径 | 说明 | 角色 |
|------|------|------|------|
| `POST` | `/invoices/apply` | 申请开票 | 所有登录用户 |
| `GET` | `/invoices` | 我的发票列表 | 所有登录用户 |
| `GET` | `/invoices/{id}` | 发票详情 | 发票申请人 |
| `GET` | `/invoices/{id}/download` | 下载发票 PDF | 发票申请人 |

---

## 运维监控 API

> **说明**: 运维监控 API 供运维和开发人员使用，用于服务健康检查、性能监控、日志查询等。
> 注意：此 API 无需 JWT 认证，但需通过 IP 白名单访问。

### 服务健康检查

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/health` | 综合健康检查（所有服务） |
| `GET` | `/api/health/business` | 业务后端健康检查 |
| `GET` | `/api/health/gateway` | 网关健康检查 |
| `GET` | `/api/health/ai` | AI 服务健康检查 |

**响应**
```json
{
  "status": "healthy",
  "timestamp": "2026-05-19T09:00:00Z",
  "services": {
    "business": {"status": "healthy", "database": "connected", "mongodb": "connected"},
    "gateway": {"status": "healthy", "clickhouse": "connected", "redis": "connected"},
    "ai": {"status": "healthy", "milvus": "connected", "openai": "connected"}
  }
}
```

### 性能指标

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/metrics/prometheus` | Prometheus 格式指标 |
| `GET` | `/api/metrics/gateway/qps` | 网关 QPS/RT |
| `GET` | `/api/metrics/database/slow-queries` | 数据库慢查询日志 |

### 日志查询

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/logs/traces` | 链路追踪日志（按 traceId 查询） |
| `GET` | `/api/logs/errors` | 错误日志聚合 |
| `POST` | `/api/logs/search` | 高级日志搜索 |

### 实例管理

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/instances` | 服务实例列表 |
| `POST` | `/api/instances/{id}/restart` | 重启实例（需确认） |
| `GET` | `/api/instances/{id}/metrics` | 实例性能指标 |

### 运维任务

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/operations/db-migrate` | 执行数据库迁移 |
| `POST` | `/api/operations/vector-rebuild` | 重新构建向量索引 |
| `POST` | `/api/operations/cache-clear` | 清除 Redis 缓存 |
| `POST` | `/api/operations/report-batch-generate` | 批量生成报告 |

---

## WebSocket 实时通信

### 连接地址

```
ws://gateway:8081/ws/assessment?token=xxx
```

### 消息协议

#### 客户端 → 服务端

```json
{
  "type": "EVENT",
  "data": {
    "sessionId": "session-uuid",
    "event": {
      "timestamp": 1716105600000,
      "eventType": "click",
      "data": {}
    }
  }
}
```

#### 服务端 → 客户端

```json
{
  "type": "ACK",
  "data": {
    "sessionId": "session-uuid",
    "accepted": true
  }
}
```

### 事件流

```
student-app ──WS CONNECT──▶ Gateway ──EVENT 消息实时写入──▶ ClickHouse/MongoDB
     ◀──ACK 确认──────────          （毫秒级延迟）
```

---

## 错误处理

### 错误响应格式

```json
{
  "code": 4001,
  "data": null,
  "message": "认证失败：Token 已过期",
  "traceId": "req-xxxxx"
}
```

### 错误码表

| 错误码 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| `0` | `200` | 成功 |
| `4001` | `401` | 认证失败 / Token 过期 |
| `4003` | `403` | 权限不足 |
| `4004` | `404` | 资源不存在 |
| `4009` | `400` | 请求参数错误 |
| `4029` | `429` | 请求频率超限 |
| `5000` | `500` | 服务器内部错误 |
| `5002` | `503` | 服务不可用 |

---

## OpenAPI 规范

完整的 OpenAPI 3.0 规范文件已生成:

| 服务 | 文件路径 |
|------|----------|
| 业务后端 (`/api/v1`) | [`docs/api/openapi-business.yaml`](docs/api/openapi-business.yaml) |
| AI 服务 (`/ai/v1`) | [`docs/api/openapi-ai.yaml`](docs/api/openapi-ai.yaml) |

---

> **文档说明**:
>
> - 所有 API 均需通过 Nginx 反向代理暴露
> - 高频采集端点由 Go 网关处理，其余由 Java 业务服务处理
> - AI 分析端点走独立路由 `/ai/v1`，可独立扩容
