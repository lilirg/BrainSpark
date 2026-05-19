# BrainSpark API 契约文档

> 版本: 1.0.0 | 最后更新: 2026-05-19 | 来源：api-design.md / middleware-design.md / teacher-web-design.md

## 目录

1. [通用规范](#通用规范)
2. [用户认证](#用户认证)
3. [用户管理](#用户管理)
4. [班级管理](#班级管理)
5. [学生档案](#学生档案)
6. [测评任务](#测评任务)
7. [行为事件采集](#行为事件采集)
8. [AI 分析与报告](#ai-分析与报告)
9. [家长端服务](#家长端服务)
10. [员工端服务](#员工端服务)
11. [运营管理](#运营管理)
12. [订单与支付](#订单与支付)
13. [订单管理](#订单管理)
14. [订阅管理](#订阅管理)
15. [发票管理](#发票管理)
16. [运维监控](#运维监控)
17. [WebSocket 实时通信](#websocket-实时通信)
18. [错误处理](#错误处理)

---

## 通用规范

### 请求格式

- 路径: RESTful 风格，所有业务 API 统一使用 `/api/v1/` 前缀（AI 服务为 `/ai/v1/`）
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

### 用户角色

| 角色 | 说明 |
|------|------|
| `ADMIN` | 系统管理员 |
| `MANAGER` | 经理 |
| `EMPLOYEE` | 员工 |
| `TEACHER` | 教师 |
| `OPERATOR` | 运营人员 |
| `PARENT` | 家长 |
| `STUDENT` | 学生 |

---

## 用户认证

#### `POST /api/v1/auth/login`

- 描述：用户登录，返回 JWT Token
- 认证：无需认证
- 请求参数：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

- 响应示例：

```json
{
  "code": 200,
  "data": {
    "accessToken": "eyJhbGc...",
    "refreshToken": "eyJhbGc...",
    "expiresIn": 7200,
    "role": "TEACHER"
  },
  "message": "ok"
}
```

#### `POST /api/v1/auth/refresh`

- 描述：刷新 Token
- 认证：无需认证
- 请求参数：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| refreshToken | string | 是 | 刷新 Token |

#### `POST /api/v1/auth/logout`

- 描述：登出，服务端注销 Token
- 认证：需要

#### `GET /api/v1/auth/me`

- 描述：获取当前登录用户信息
- 认证：需要

---

## 用户管理

基础路径: `/api/v1/users`

#### `GET /api/v1/users`

- 描述：用户列表（分页）
- 认证：需要 | 角色：`ADMIN`, `MANAGER`, `EMPLOYEE`, `TEACHER`

#### `GET /api/v1/users/{id}`

- 描述：获取用户详情
- 认证：需要

#### `POST /api/v1/users`

- 描述：创建用户
- 认证：需要 | 角色：`ADMIN`, `MANAGER`, `EMPLOYEE`
- 请求参数：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |
| role | string | 是 | 角色 |
| realName | string | 是 | 真实姓名 |
| age | int | 否 | 年龄 |
| grade | string | 否 | 年级 |

#### `PUT /api/v1/users/{id}`

- 描述：更新用户信息
- 认证：需要

#### `DELETE /api/v1/users/{id}`

- 描述：停用用户
- 认证：需要 | 角色：`ADMIN`

#### `POST /api/v1/users/{id}/reset-password`

- 描述：重置用户密码
- 认证：需要 | 角色：`ADMIN`, `MANAGER`, `EMPLOYEE`

#### `POST /api/v1/users/{id}/activate`

- 描述：激活用户账号
- 认证：需要

#### `POST /api/v1/users/{id}/deactivate`

- 描述：停用了用户账号
- 认证：需要

#### `POST /api/v1/users/{id}/bind-parent`

- 描述：绑定亲子关系
- 认证：需要 | 角色：`ADMIN`, `TEACHER`

#### `POST /api/v1/users/{id}/note`

- 描述：添加员工备注
- 认证：需要

---

## 班级管理

基础路径: `/api/v1/classes`

#### `GET /api/v1/classes`

- 描述：班级列表（分页）
- 认证：需要 | 角色：`TEACHER`

#### `POST /api/v1/classes`

- 描述：创建班级
- 认证：需要 | 角色：`TEACHER`
- 请求参数：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 班级名称 |
| grade | int | 是 | 年级 |
| teacherId | string | 是 | 教师 ID |
| description | string | 否 | 描述 |

#### `GET /api/v1/classes/{id}`

- 描述：班级详情
- 认证：需要 | 角色：`TEACHER`

#### `PUT /api/v1/classes/{id}`

- 描述：更新班级
- 认证：需要 | 角色：`TEACHER`

#### `DELETE /api/v1/classes/{id}`

- 描述：删除班级
- 认证：需要 | 角色：`TEACHER`

#### `POST /api/v1/classes/{id}/members`

- 描述：添加学生到班级
- 认证：需要 | 角色：`TEACHER`

#### `DELETE /api/v1/classes/{id}/members/{studentId}`

- 描述：从班级移除学生
- 认证：需要 | 角色：`TEACHER`

---

## 学生档案

基础路径: `/api/v1/students`

#### `GET /api/v1/students`

- 描述：学生列表（按班级筛选，分页）
- 认证：需要 | 角色：`TEACHER`

#### `GET /api/v1/students/{id}`

- 描述：学生档案详情
- 认证：需要 | 角色：`TEACHER`, `PARENT`

#### `PUT /api/v1/students/{id}/profile`

- 描述：更新学生档案
- 认证：需要 | 角色：`TEACHER`, `PARENT`

#### `GET /api/v1/students/{id}/growth`

- 描述：获取学生成长趋势数据
- 认证：需要 | 角色：`TEACHER`, `PARENT`
- 响应示例：

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
  },
  "message": "ok"
}
```

---

## 测评任务

基础路径: `/api/v1/assessments`

#### `GET /api/v1/assessments/tasks`

- 描述：测评任务列表
- 认证：需要 | 角色：`TEACHER`

#### `POST /api/v1/assessments/tasks`

- 描述：创建测评任务
- 认证：需要 | 角色：`TEACHER`

#### `GET /api/v1/assessments/tasks/{id}`

- 描述：测评任务详情
- 认证：需要 | 角色：`TEACHER`

#### `PUT /api/v1/assessments/tasks/{id}`

- 描述：更新测评任务
- 认证：需要 | 角色：`TEACHER`

#### `DELETE /api/v1/assessments/tasks/{id}`

- 描述：删除测评任务
- 认证：需要 | 角色：`TEACHER`

#### `GET /api/v1/assessments/tasks/today`

- 描述：今日待测任务
- 认证：需要 | 角色：`STUDENT`

#### `GET /api/v1/assessments/results`

- 描述：测评结果列表（分页）
- 认证：需要 | 角色：`TEACHER`

#### `GET /api/v1/assessments/results/{id}`

- 描述：测评结果详情
- 认证：需要 | 角色：`TEACHER`, `PARENT`

---

## 行为事件采集

基础路径: `/api/v1/events`（由 Go 网关处理）

#### `POST /api/v1/events/batch`

- 描述：批量提交行为事件
- 认证：需要

#### `POST /api/v1/events/ws`

- 描述：WebSocket 事件流
- 认证：需要 | 角色：`STUDENT`

---

## AI 分析与报告

> 注意: AI 分析 API 使用独立路由 `/ai/v1/`

#### `POST /ai/v1/assessments/analyze`

- 描述：分析测评数据，生成认知维度评分
- 认证：需要 | 角色：`TEACHER`
- 请求参数：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| student_id | string | 是 | 学生 ID |
| events | array | 是 | 事件数组 |

- 响应示例：

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

#### `POST /ai/v1/reports/generate`

- 描述：生成 AI 分析报告
- 认证：需要 | 角色：`TEACHER`
- 请求参数：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| student_id | string | 是 | 学生 ID |
| assessment | object | 是 | 测评结果 |
| context | string | 否 | 上下文信息 |

#### `POST /ai/v1/knowledge/index`

- 描述：索引知识库文档
- 认证：需要 | 角色：`ADMIN`

### 报告管理

基础路径: `/api/v1/reports`

#### `GET /api/v1/reports`

- 描述：报告列表（分页）
- 认证：需要 | 角色：`TEACHER`, `PARENT`

#### `GET /api/v1/reports/{id}`

- 描述：报告详情
- 认证：需要 | 角色：`TEACHER`, `PARENT`

#### `POST /api/v1/reports/{id}/regenerate`

- 描述：重新生成报告
- 认证：需要 | 角色：`TEACHER`

#### `GET /api/v1/reports/{id}/download`

- 描述：下载报告（PDF）
- 认证：需要 | 角色：`PARENT`

#### `POST /api/v1/reports/{id}/share`

- 描述：生成报告分享链接
- 认证：需要 | 角色：`TEACHER`

---

## 家长端服务

基础路径: `/api/v1/parent`

#### `GET /api/v1/parent/children`

- 描述：关联子女列表
- 认证：需要 | 角色：`PARENT`

#### `POST /api/v1/parent/children/bind`

- 描述：绑定子女
- 认证：需要 | 角色：`PARENT`

#### `DELETE /api/v1/parent/children/{childId}`

- 描述：解除绑定
- 认证：需要 | 角色：`PARENT`

#### `GET /api/v1/parent/dashboard/{childId}`

- 描述：子女仪表板数据
- 认证：需要 | 角色：`PARENT`

#### `GET /api/v1/parent/usage`

- 描述：使用时长统计
- 认证：需要 | 角色：`PARENT`

#### `PUT /api/v1/parent/settings`

- 描述：家长设置
- 认证：需要 | 角色：`PARENT`

---

## 员工端服务

基础路径: `/api/v1/employee`

### 工作台

#### `GET /api/v1/employee/dashboard/stats`

- 描述：工作概览统计
- 认证：需要 | 角色：`EMPLOYEE`, `MANAGER`

#### `GET /api/v1/employee/dashboard/todos`

- 描述：待办事项
- 认证：需要 | 角色：`EMPLOYEE`, `MANAGER`

#### `GET /api/v1/employee/dashboard/activities`

- 描述：最近活动
- 认证：需要 | 角色：`EMPLOYEE`, `MANAGER`

#### `GET /api/v1/employee/dashboard/user-trend`

- 描述：用户趋势数据
- 认证：需要 | 角色：`EMPLOYEE`, `MANAGER`

### 家长服务

#### `GET /api/v1/employee/parents`

- 描述：家长列表
- 认证：需要 | 角色：`EMPLOYEE`, `MANAGER`

#### `GET /api/v1/employee/parents/{id}`

- 描述：家长详情
- 认证：需要 | 角色：`EMPLOYEE`, `MANAGER`

#### `POST /api/v1/employee/parents/{id}/guidance`

- 描述：记录服务日志
- 认证：需要 | 角色：`EMPLOYEE`

#### `POST /api/v1/employee/parents/{id}/follow-up`

- 描述：添加跟进记录
- 认证：需要 | 角色：`EMPLOYEE`

### 学生服务

#### `GET /api/v1/employee/students`

- 描述：学生列表
- 认证：需要 | 角色：`EMPLOYEE`, `MANAGER`

#### `GET /api/v1/employee/students/{id}`

- 描述：学生详情
- 认证：需要 | 角色：`EMPLOYEE`, `MANAGER`

#### `POST /api/v1/employee/students/{id}/guide-assessment`

- 描述：引导测评
- 认证：需要 | 角色：`EMPLOYEE`

#### `POST /api/v1/employee/students/{id}/remind`

- 描述：发送提醒
- 认证：需要 | 角色：`EMPLOYEE`

### 测评服务

#### `GET /api/v1/employee/assessments/statistics`

- 描述：服务统计数据
- 认证：需要 | 角色：`EMPLOYEE`

#### `POST /api/v1/employee/assessments/{id}/guide`

- 描述：发起测评引导
- 认证：需要 | 角色：`EMPLOYEE`

#### `POST /api/v1/employee/assessments/retry`

- 描述：重新尝试测评
- 认证：需要 | 角色：`EMPLOYEE`

### 报告协助

#### `GET /api/v1/employee/reports`

- 描述：报告列表（员工视角）
- 认证：需要 | 角色：`EMPLOYEE`

#### `GET /api/v1/employee/reports/{id}`

- 描述：报告详情（员工视角）
- 认证：需要 | 角色：`EMPLOYEE`

#### `POST /api/v1/employee/reports/{id}/interpret`

- 描述：记录解读协助
- 认证：需要 | 角色：`EMPLOYEE`

### 消息中心

#### `GET /api/v1/employee/messages`

- 描述：已发送消息记录
- 认证：需要 | 角色：`EMPLOYEE`, `MANAGER`

#### `POST /api/v1/employee/messages/send`

- 描述：发送消息
- 认证：需要 | 角色：`EMPLOYEE`, `MANAGER`

#### `GET /api/v1/employee/messages/templates`

- 描述：消息模板列表（经理）
- 认证：需要 | 角色：`MANAGER`

#### `POST /api/v1/employee/messages/templates`

- 描述：新建消息模板（经理）
- 认证：需要 | 角色：`MANAGER`

#### `PUT /api/v1/employee/messages/templates/{id}`

- 描述：编辑消息模板（经理）
- 认证：需要 | 角色：`MANAGER`

#### `DELETE /api/v1/employee/messages/templates/{id}`

- 描述：删除消息模板（经理）
- 认证：需要 | 角色：`MANAGER`

#### `PUT /api/v1/employee/messages/{id}/mark-read`

- 描述：标记消息已读
- 认证：需要 | 角色：`EMPLOYEE`

---

## 运营管理

### 内容管理

基础路径: `/api/v1/admin/content`

#### `GET /api/v1/admin/content/assessments`

- 描述：测评量表列表
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `POST /api/v1/admin/content/assessments`

- 描述：上架新测评
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `PUT /api/v1/admin/content/assessments/{id}`

- 描述：更新测评配置
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `POST /api/v1/admin/content/assessments/{id}/publish`

- 描述：发布测评
- 认证：需要 | 角色：`ADMIN`

#### `POST /api/v1/admin/content/assessments/{id}/hide`

- 描述：下架测评
- 认证：需要 | 角色：`ADMIN`

### 知识库管理

基础路径: `/api/v1/admin/knowledge`

#### `GET /api/v1/admin/knowledge/docs`

- 描述：知识库文档列表（分页）
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `POST /api/v1/admin/knowledge/docs`

- 描述：新增知识文档
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `PUT /api/v1/admin/knowledge/docs/{id}`

- 描述：更新知识文档
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `DELETE /api/v1/admin/knowledge/docs/{id}`

- 描述：删除知识文档
- 认证：需要 | 角色：`ADMIN`

#### `POST /api/v1/admin/knowledge/rebuild`

- 描述：重新构建向量索引
- 认证：需要 | 角色：`ADMIN`

### 数据统计

基础路径: `/api/v1/admin/analytics`

#### `GET /api/v1/admin/analytics/dashboard`

- 描述：运营仪表板总览
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `GET /api/v1/admin/analytics/users`

- 描述：用户增长数据
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `GET /api/v1/admin/analytics/assessments`

- 描述：测评完成统计
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `GET /api/v1/admin/analytics/reports`

- 描述：报告生成统计
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `GET /api/v1/admin/analytics/revenue`

- 描述：收入统计
- 认证：需要 | 角色：`ADMIN`

### 机构合作管理

基础路径: `/api/v1/admin/partners`

#### `GET /api/v1/admin/partners`

- 描述：合作机构列表
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `POST /api/v1/admin/partners`

- 描述：新增合作机构
- 认证：需要 | 角色：`ADMIN`

#### `GET /api/v1/admin/partners/{id}`

- 描述：机构详情
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `PUT /api/v1/admin/partners/{id}`

- 描述：更新机构信息
- 认证：需要 | 角色：`ADMIN`

#### `GET /api/v1/admin/partners/{id}/analytics`

- 描述：机构数据看板
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

### 审核管理

基础路径: `/api/v1/admin/moderation`

#### `GET /api/v1/admin/moderation/reports`

- 描述：报告反馈列表
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `PUT /api/v1/admin/moderation/reports/{id}`

- 描述：处理反馈
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `GET /api/v1/admin/moderation/contents`

- 描述：用户生成内容审核
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `POST /api/v1/admin/moderation/contents/{id}/approve`

- 描述：通过审核
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `POST /api/v1/admin/moderation/contents/{id}/reject`

- 描述：驳回审核
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

### 系统配置

基础路径: `/api/v1/admin/config`

#### `GET /api/v1/admin/config`

- 描述：获取所有配置项
- 认证：需要 | 角色：`ADMIN`

#### `PUT /api/v1/admin/config/{key}`

- 描述：更新配置项
- 认证：需要 | 角色：`ADMIN`

#### `POST /api/v1/admin/config/batch`

- 描述：批量更新配置
- 认证：需要 | 角色：`ADMIN`

### 通知管理

基础路径: `/api/v1/admin/notifications`

#### `GET /api/v1/admin/notifications`

- 描述：通知列表（分页）
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `POST /api/v1/admin/notifications`

- 描述：创建通知
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `PUT /api/v1/admin/notifications/{id}`

- 描述：更新通知
- 认证：需要 | 角色：`ADMIN`

#### `POST /api/v1/admin/notifications/{id}/send`

- 描述：发送通知
- 认证：需要 | 角色：`ADMIN`, `OPERATOR`

#### `DELETE /api/v1/admin/notifications/{id}`

- 描述：删除通知
- 认证：需要 | 角色：`ADMIN`

### 员工管理

#### `GET /api/v1/admin/employees`

- 描述：员工列表
- 认证：需要 | 角色：`ADMIN`, `MANAGER`

#### `GET /api/v1/admin/employees/{id}`

- 描述：员工详情
- 认证：需要 | 角色：`ADMIN`, `MANAGER`

#### `PUT /api/v1/admin/employees/{id}/role`

- 描述：员工角色变更
- 认证：需要 | 角色：`ADMIN`

#### `GET /api/v1/admin/employees/{id}/stats`

- 描述：员工服务统计数据
- 认证：需要 | 角色：`ADMIN`, `MANAGER`

#### `GET /api/v1/admin/employees/{id}/audit-log`

- 描述：员工操作审计日志
- 认证：需要 | 角色：`ADMIN`, `MANAGER`

#### `GET /api/v1/admin/team/statistics`

- 描述：团队统计数据
- 认证：需要 | 角色：`ADMIN`, `MANAGER`

---

## 商品管理

基础路径: `/api/v1/shop`

#### `GET /api/v1/shop/products`

- 描述：商品列表（公开发布的商品）
- 认证：需要

#### `GET /api/v1/shop/products/{id}`

- 描述：商品详情
- 认证：需要

#### `GET /api/v1/shop/packages`

- 描述：套餐列表
- 认证：需要

#### `GET /api/v1/shop/redeem`

- 描述：优惠券兑换
- 认证：需要

#### `GET /api/v1/plans`

- 描述：订阅方案列表
- 认证：无需

#### `GET /api/v1/plans/available`

- 描述：获取可用方案（含活动折扣）
- 认证：无需

#### `GET /api/v1/promotions/apply`

- 描述：验证活动码可用性
- 认证：无需

---

## 订单管理

基础路径: `/api/v1/orders`

#### `POST /api/v1/orders`

- 描述：创建订单
- 认证：需要

#### `GET /api/v1/orders`

- 描述：我的订单列表（分页）
- 认证：需要

#### `GET /api/v1/orders/{id}`

- 描述：订单详情
- 认证：需要

#### `POST /api/v1/orders/{id}/cancel`

- 描述：取消订单
- 认证：需要

#### `GET /api/v1/orders/{id}/status`

- 描述：查询订单状态
- 认证：需要

### 支付回调

> 注意: 这是第三方支付平台的回调地址，客户端无需调用

#### `POST /api/v1/payments/wechat/callback`

- 描述：微信支付回调

#### `POST /api/v1/payments/alipay/callback`

- 描述：支付宝回调

#### `POST /api/v1/payments/verify`

- 描述：验证支付结果
- 认证：需要

---

## 订阅管理

基础路径: `/api/v1/subscription`

#### `GET /api/v1/subscription/status`

- 描述：当前订阅状态
- 认证：需要

#### `GET /api/v1/subscription/history`

- 描述：订阅历史
- 认证：需要

#### `POST /api/v1/subscription/cancel`

- 描述：取消订阅（下周期生效）
- 认证：需要

#### `POST /api/v1/subscription/reactivate`

- 描述：重新激活订阅
- 认证：需要

#### `GET /api/v1/subscription/benefits`

- 描述：权益清单
- 认证：需要

---

## 发票管理

基础路径: `/api/v1/invoices`

#### `POST /api/v1/invoices/apply`

- 描述：申请开票
- 认证：需要

#### `GET /api/v1/invoices`

- 描述：我的发票列表
- 认证：需要

#### `GET /api/v1/invoices/{id}`

- 描述：发票详情
- 认证：需要

#### `GET /api/v1/invoices/{id}/download`

- 描述：下载发票 PDF
- 认证：需要

---

## 运维监控

> 说明: 无需 JWT 认证，需通过 IP 白名单访问

#### `GET /api/health`

- 描述：综合健康检查（所有服务）

#### `GET /api/health/business`

- 描述：业务后端健康检查

#### `GET /api/health/gateway`

- 描述：网关健康检查

#### `GET /api/health/ai`

- 描述：AI 服务健康检查

#### `GET /api/metrics/prometheus`

- 描述：Prometheus 格式指标

#### `GET /api/metrics/gateway/qps`

- 描述：网关 QPS/RT

#### `GET /api/metrics/database/slow-queries`

- 描述：数据库慢查询日志

#### `GET /api/logs/traces`

- 描述：链路追踪日志

#### `GET /api/logs/errors`

- 描述：错误日志聚合

#### `POST /api/logs/search`

- 描述：高级日志搜索

#### `GET /api/instances`

- 描述：服务实例列表

#### `POST /api/instances/{id}/restart`

- 描述：重启实例

#### `GET /api/instances/{id}/metrics`

- 描述：实例性能指标

#### `POST /api/operations/db-migrate`

- 描述：执行数据库迁移

#### `POST /api/operations/vector-rebuild`

- 描述：重新构建向量索引

#### `POST /api/operations/cache-clear`

- 描述：清除 Redis 缓存

#### `POST /api/operations/report-batch-generate`

- 描述：批量生成报告

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

> **文档说明**:
>
> - 所有 API 均需通过 Nginx 反向代理暴露
> - 高频采集端点由 Go 网关处理，其余由 Java 业务服务处理
> - AI 分析端点走独立路由 `/ai/v1`，可独立扩容