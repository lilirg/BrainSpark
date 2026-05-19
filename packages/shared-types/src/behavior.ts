export interface BehaviorRecord {
  id: string
  userId: string
  assessmentId: string
  timestamp: number
  eventType: string
  data: Record<string, any>
}