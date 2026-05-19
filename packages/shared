export enum AssessmentType {
  SCHULTE_GRID = 'SCHULTE_GRID',
  NUMBER_SPAN = 'NUMBER_SPAN',
  PATTERN_RECOGNITION = 'PATTERN_RECOGNITION',
}

export interface AssessmentTask {
  id: string
  name: string
  type: AssessmentType
  description: string
  difficulty: number
  duration: number
  config: Record<string, any>
  createdAt: string
}

export interface AssessmentResult {
  id: string
  userId: string
  taskId: string
  taskType: AssessmentType
  score: number
  percentile: number
  accuracy: number
  avgReactionTime: number
  maxReactionTime: number
  minReactionTime: number
  completedAt: string
}

export enum BehaviorEventType {
  CLICK = 'click',
  HOVER = 'hover',
  KEY_PRESS = 'keypress',
  ASSESSMENT_START = 'assessment_start',
  ASSESSMENT_END = 'assessment_end',
  ASSESSMENT_ABORT = 'assessment_abort',
}

export interface BehaviorRecord {
  id: string
  userId: string
  assessmentId: string
  timestamp: number
  eventType: BehaviorEventType
  data: Record<string, any>
}