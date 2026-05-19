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
10. [WebSocket 实时通信](#websocket-实时通信)
11. [错误处理](#错误处理)
12. [OpenAPI 规范](#openapi-规范)

---

## 概述

BrainSpark 采用微服务架构，API 按服务域划分：

| 服务 | 端口 | 路由前缀 | 说明 |
|------|------|----------|------|
| 业务后端 | 8080 | `/api/v1` | 用户、班级、测评任务、报告 CRUD |
| 高并发网关 | 8081 | `/api/v1` | 游戏结果实时采集、WebSocket |
| AI 服务 | 8001 | `/ai/v1` | 认知分析、报告生成、RAG 检索 |

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
