export interface InputEvent {
  type: 'click' | 'touch' | 'keyboard'
  x?: number
  y?: number
  key?: string
  timestamp: number
  target?: string
}

export type InputCallback = (event: InputEvent) => void

export class InputHandler {
  private canvas: HTMLCanvasElement
  private callback: InputCallback | null = null
  private boundClickHandler: (e: MouseEvent) => void
  private boundTouchHandler: (e: TouchEvent) => void
  private boundKeyHandler: (e: KeyboardEvent) => void

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas
    this.boundClickHandler = this.handleClick.bind(this)
    this.boundTouchHandler = this.handleTouch.bind(this)
    this.boundKeyHandler = this.handleKey.bind(this)
  }

  setCallback(callback: InputCallback) {
    this.callback = callback
  }

  enable() {
    this.canvas.addEventListener('click', this.boundClickHandler)
    this.canvas.addEventListener('touchstart', this.boundTouchHandler, { passive: true })
    document.addEventListener('keydown', this.boundKeyHandler)
  }

  disable() {
    this.canvas.removeEventListener('click', this.boundClickHandler)
    this.canvas.removeEventListener('touchstart', this.boundTouchHandler)
    document.removeEventListener('keydown', this.boundKeyHandler)
  }

  private handleClick(e: MouseEvent) {
    const rect = this.canvas.getBoundingClientRect()
    this.emit({
      type: 'click',
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
      timestamp: performance.now() * 1000
    })
  }

  private handleTouch(e: TouchEvent) {
    if (e.touches.length > 0) {
      const touch = e.touches[0]
      const rect = this.canvas.getBoundingClientRect()
      this.emit({
        type: 'touch',
        x: touch.clientX - rect.left,
        y: touch.clientY - rect.top,
        timestamp: performance.now() * 1000
      })
    }
  }

  private handleKey(e: KeyboardEvent) {
    this.emit({
      type: 'keyboard',
      key: e.key,
      timestamp: performance.now() * 1000
    })
  }

  private emit(event: InputEvent) {
    this.callback?.(event)
  }

  destroy() {
    this.disable()
    this.callback = null
  }
}