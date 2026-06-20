export class MicroTimer {
  private startTime: number = 0
  private elapsed: number = 0
  private running: boolean = false

  start() {
    this.startTime = performance.now()
    this.running = true
  }

  stop(): number {
    if (this.running) {
      this.elapsed = performance.now() - this.startTime
      this.running = false
    }
    return this.getMicroseconds()
  }

  pause() {
    if (this.running) {
      this.elapsed += performance.now() - this.startTime
      this.running = false
    }
  }

  resume() {
    if (!this.running) {
      this.startTime = performance.now()
      this.running = true
    }
  }

  reset() {
    this.startTime = 0
    this.elapsed = 0
    this.running = false
  }

  getMilliseconds(): number {
    if (this.running) {
      return performance.now() - this.startTime + this.elapsed
    }
    return this.elapsed
  }

  getMicroseconds(): number {
    return this.getMilliseconds() * 1000
  }

  isRunning(): boolean {
    return this.running
  }
}