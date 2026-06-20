import type { BehaviorEvent, DeviceInfo } from '@brainspark/shared-types'

export class EventCollector {
  private buffer: BehaviorEvent[] = []
  private maxBufferSize: number = 100
  private flushInterval: number = 5000 // 5秒
  private timerId: ReturnType<typeof setInterval> | null = null
  private apiUrl: string
  private sessionId: string
  private studentId: string

  constructor(studentId: string, sessionId: string) {
    this.studentId = studentId
    this.sessionId = sessionId
    this.apiUrl = import.meta.env.VITE_EVENT_API_URL || '/api/v1/events/batch'
  }

  start() {
    this.timerId = setInterval(() => this.flush(), this.flushInterval)
  }

  stop() {
    if (this.timerId) {
      clearInterval(this.timerId)
      this.timerId = null
    }
    this.flush() // 停止时立即刷新
  }

  collect(event: Omit<BehaviorEvent, 'id' | 'sessionId' | 'studentId' | 'createdAt'>) {
    const behaviorEvent: BehaviorEvent = {
      id: this.generateId(),
      sessionId: this.sessionId,
      studentId: this.studentId,
      type: event.type,
      timestamp: event.timestamp,
      data: event.data,
      deviceInfo: event.deviceInfo || this.getDeviceInfo(),
      createdAt: new Date().toISOString()
    }

    this.buffer.push(behaviorEvent)

    if (this.buffer.length >= this.maxBufferSize) {
      this.flush()
    }
  }

  private async flush() {
    if (this.buffer.length === 0) return

    const events = [...this.buffer]
    this.buffer = []

    try {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ events })
      })

      if (!response.ok) {
        // 失败时重新加入缓冲区
        this.buffer.unshift(...events)
        if (this.buffer.length > this.maxBufferSize * 2) {
          this.buffer = this.buffer.slice(-this.maxBufferSize)
        }
      }
    } catch (error) {
      console.error('事件发送失败，暂存到本地:', error)
      // 保存到 IndexedDB
      this.saveToIndexedDB(events)
    }
  }

  private async saveToIndexedDB(events: BehaviorEvent[]) {
    try {
      const request = indexedDB.open('BrainSparkEvents', 1)

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result
        if (!db.objectStoreNames.contains('pending_events')) {
          db.createObjectStore('pending_events', { keyPath: 'id' })
        }
      }

      request.onsuccess = (event) => {
        const db = (event.target as IDBOpenDBRequest).result
        const tx = db.transaction('pending_events', 'readwrite')
        const store = tx.objectStore('pending_events')

        for (const event of events) {
          store.add(event)
        }
      }
    } catch (error) {
      console.error('IndexedDB 存储失败:', error)
    }
  }

  private getDeviceInfo(): DeviceInfo {
    return {
      userAgent: navigator.userAgent,
      screenResolution: `${window.screen.width}x${window.screen.height}`,
      deviceType: this.detectDeviceType(),
      browser: this.detectBrowser(),
      os: this.detectOS()
    }
  }

  private detectDeviceType(): 'MOBILE' | 'TABLET' | 'DESKTOP' {
    const ua = navigator.userAgent
    if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) return 'TABLET'
    if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua)) return 'MOBILE'
    return 'DESKTOP'
  }

  private detectBrowser(): string {
    const ua = navigator.userAgent
    if (ua.includes('Chrome')) return 'Chrome'
    if (ua.includes('Firefox')) return 'Firefox'
    if (ua.includes('Safari')) return 'Safari'
    if (ua.includes('Edge')) return 'Edge'
    return 'Unknown'
  }

  private detectOS(): string {
    const ua = navigator.userAgent
    if (ua.includes('Windows')) return 'Windows'
    if (ua.includes('Mac OS')) return 'macOS'
    if (ua.includes('Linux')) return 'Linux'
    if (ua.includes('Android')) return 'Android'
    if (ua.includes('iOS')) return 'iOS'
    return 'Unknown'
  }

  private generateId(): string {
    return `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
}