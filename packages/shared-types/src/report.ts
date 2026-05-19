export interface CapabilityRadar {
  attention: number
  memory: number
  logic: number
  language: number
  spatial: number
  executiveFunction: number
}

export interface AIReport {
  id: string
  userId: string
  assessmentId: string
  capabilityRadar: CapabilityRadar
  summary: string
  strengths: string[]
  weaknesses: string[]
  recommendations: string[]
  trainingPlan: TrainingPlanItem[]
  generatedAt: string
  modelVersion: string
}

export interface TrainingPlanItem {
  id: string
  title: string
  description: string
  type: string
  duration: number
  frequency: string
  difficulty: number
}