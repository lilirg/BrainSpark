// BrainSpark 共享类型定义
// 基于 docs/architecture/data-model.md 和 docs/architecture/api-contract.md

// ==================== 用户角色枚举 ====================

export enum UserRole {
  ADMIN = 'ADMIN',
  MANAGER = 'MANAGER',
  EMPLOYEE = 'EMPLOYEE',
  TEACHER = 'TEACHER',
  PARENT = 'PARENT',
  STUDENT = 'STUDENT'
}

// ==================== 统一响应格式 ====================

export interface ApiResponse<T = any> {
  code: number
  data: T
  message: string
}

// ==================== 分页 ====================

export interface PaginatedRequest {
  page: number
  size: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
}

// ==================== 用户实体 ====================

export interface User {
  id: string
  username: string
  email: string
  phone?: string
  role: UserRole
  status: 'ACTIVE' | 'INACTIVE' | 'LOCKED'
  createdAt: string
  updatedAt: string
}

export interface UserInfo {
  id: string
  name: string
  age: number
  grade: string
  avatar?: string
  createdAt: string
  updatedAt: string
}

// ==================== 学生实体 ====================

export interface Student {
  id: string
  studentCode: string
  name: string
  gender: 'MALE' | 'FEMALE' | 'OTHER'
  age: number
  grade: string
  classId?: string
  parentId?: string
  profile?: StudentProfile
  createdAt: string
  updatedAt: string
}

export interface StudentProfile {
  cognitiveDimensions?: CognitiveDimension[]
  lastAssessmentDate?: string
  totalAssessments: number
  growthMetrics?: GrowthMetrics
}

export interface GrowthMetrics {
  overallScore: number
  trend: 'UP' | 'DOWN' | 'STABLE'
  lastUpdated: string
}

// ==================== 认知维度 ====================

export interface CognitiveDimension {
  name: string
  score: number
  percentile: number
  level: 'HIGH' | 'AVERAGE' | 'LOW'
}

// ==================== 班级实体 ====================

export interface Class {
  id: string
  name: string
  grade: string
  teacherId?: string
  students: Student[]
  createdAt: string
  updatedAt: string
}

// ==================== 测评相关 ====================

export enum AssessmentType {
  SCHULTER = 'SCHULTER',
  DIGITAL_SPAN = 'DIGITAL_SPAN',
  PATTERN_REASONING = 'PATTERN_REASONING'
}

export interface AssessmentTask {
  id: string
  type: AssessmentType
  title: string
  description: string
  assignedClassId?: string
  assignedStudentIds?: string[]
  scheduledAt: string
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'
  createdAt: string
  updatedAt: string
}

export interface AssessmentResult {
  id: string
  sessionId: string
  studentId: string
  type: AssessmentType
  scores: Record<string, number>
  cognitiveDimensions: CognitiveDimension[]
  status: 'PROCESSING' | 'COMPLETED' | 'FAILED'
  createdAt: string
  completedAt?: string
}

// ==================== 报告 ====================

export interface Report {
  id: string
  studentId: string
  type: 'ASSESSMENT' | 'GROWTH' | 'CUSTOM'
  title: string
  content: string
  pdfUrl?: string
  shareCode?: string
  status: 'DRAFT' | 'COMPLETED' | 'SHARED'
  createdAt: string
  updatedAt: string
}

// ==================== 行为事件 ====================

export interface BehaviorEvent {
  id: string
  sessionId: string
  studentId: string
  type: 'CLICK' | 'MOVE' | 'KEYDOWN' | 'KEYUP' | 'TOUCH' | 'GAME_START' | 'GAME_END'
  timestamp: number
  data?: Record<string, any>
  deviceInfo?: DeviceInfo
  createdAt: string
}

export interface DeviceInfo {
  userAgent: string
  screenResolution: string
  deviceType: 'MOBILE' | 'TABLET' | 'DESKTOP'
  browser: string
  os: string
}