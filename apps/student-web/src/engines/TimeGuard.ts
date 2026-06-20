export interface TimeGuardConfig {
  dailyLimitMinutes: number
  nightStartHour: number
  nightEndHour: number
  breakIntervalMinutes: number
  breakDurationMinutes: number
}

export type TimeGuardEvent = 'limit_reached' | 'night_time' | 'break_time' | 'time_warning'

export type TimeGuardCallback = (event: TimeGuardEvent, data?: any) => void

export class TimeGuard {
  private config: TimeGuardConfig
  private dailyUsage: number = 0
  private lastBreakTime: number = 0
  private callback: TimeGuardCallback | null = null
  private checkInterval: ReturnType<typeof setInterval> | null = null

  constructor(config?: Partial<TimeGuardConfig>) {
    this.config = {
      dailyLimitMinutes: config?.dailyLimitMinutes || 40,
      nightStartHour: config?.nightStartHour || 22,
      nightEndHour: config?.nightEndHour || 6,
      breakIntervalMinutes: config?.breakIntervalMinutes || 20,
      breakDurationMinutes: config?.breakDurationMinutes || 5
    }
    this.loadUsage()
  }

  setCallback(callback: TimeGuardCallback) {
    this.callback = callback
  }

  start() {
    this.checkInterval = setInterval(() => this.check(), 60000) // 每分钟检查
    this.check()
  }

  stop() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval)
      this.checkInterval = null
    }
  }

  private check() {
    // 检查夜间禁用
    if (this.isNightTime()) {
      this.callback?.('night_time', {
        message: `夜间 ${this.config.nightStartHour}:00 - ${this.config.nightEndHour}:00 无法使用`
      })
      return
    }

    // 检查每日限制
    if (this.dailyUsage >= this.config.dailyLimitMinutes) {
      this.callback?.('limit_reached', {
        message: `今日使用时间已达 ${this.config.dailyLimitMinutes} 分钟`
      })
      return
    }

    // 检查休息提醒
    const now = Date.now()
    if (now - this.lastBreakTime > this.config.breakIntervalMinutes * 60 * 1000) {
      this.callback?.('break_time', {
        message: `已连续使用 ${this.config.breakIntervalMinutes} 分钟，建议休息 ${this.config.breakDurationMinutes} 分钟`
      })
      this.lastBreakTime = now
    }

    // 时间预警
    const remaining = this.config.dailyLimitMinutes - this.dailyUsage
    if (remaining <= 5 && remaining > 0) {
      this.callback?.('time_warning', {
        message: `剩余使用时间: ${remaining} 分钟`,
        remaining
      })
    }
  }

  addUsage(minutes: number) {
    this.dailyUsage += minutes
    this.saveUsage()
  }

  getRemainingTime(): number {
    return Math.max(0, this.config.dailyLimitMinutes - this.dailyUsage)
  }

  isNightTime(): boolean {
    const hour = new Date().getHours()
    if (this.config.nightStartHour <= this.config.nightEndHour) {
      return hour >= this.config.nightStartHour && hour < this.config.nightEndHour
    }
    return hour >= this.config.nightStartHour || hour < this.config.nightEndHour
  }

  canPlay(): boolean {
    return !this.isNightTime() && this.dailyUsage < this.config.dailyLimitMinutes
  }

  private loadUsage() {
    try {
      const saved = localStorage.getItem('brainspark_daily_usage')
      if (saved) {
        const data = JSON.parse(saved)
        const today = new Date().toDateString()
        if (data.date === today) {
          this.dailyUsage = data.usage
        } else {
          this.dailyUsage = 0
          this.saveUsage()
        }
      }
    } catch {
      this.dailyUsage = 0
    }
  }

  private saveUsage() {
    try {
      localStorage.setItem('brainspark_daily_usage', JSON.stringify({
        date: new Date().toDateString(),
        usage: this.dailyUsage
      }))
    } catch {
      console.error('保存使用时间失败')
    }
  }
}