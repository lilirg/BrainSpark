import { Application, Container, Graphics, Text, TextStyle } from 'pixi.js'

export interface GameConfig {
  width: number
  height: number
  backgroundColor?: number
  antialias?: boolean
}

export interface GameState {
  isRunning: boolean
  isPaused: boolean
  startTime: number
  elapsedTime: number
  score: number
}

export interface GameEvent {
  type: string
  timestamp: number
  data?: Record<string, any>
}

export abstract class BaseGame {
  protected app: Application
  protected stage: Container
  protected state: GameState
  protected events: GameEvent[] = []
  protected onEventCallback?: (event: GameEvent) => void

  constructor(config: GameConfig) {
    this.app = new Application({
      width: config.width,
      height: config.height,
      backgroundColor: config.backgroundColor || 0x1a1a2e,
      antialias: config.antialias ?? true
    })

    this.stage = new Container()
    this.app.stage.addChild(this.stage)

    this.state = {
      isRunning: false,
      isPaused: false,
      startTime: 0,
      elapsedTime: 0,
      score: 0
    }
  }

  get view(): HTMLCanvasElement {
    return this.app.view as HTMLCanvasElement
  }

  get ticker() {
    return this.app.ticker
  }

  setEventCallback(callback: (event: GameEvent) => void) {
    this.onEventCallback = callback
  }

  protected recordEvent(type: string, data?: Record<string, any>) {
    const event: GameEvent = {
      type,
      timestamp: performance.now() * 1000, // 微秒级时间戳
      data
    }
    this.events.push(event)
    this.onEventCallback?.(event)
  }

  abstract init(): Promise<void>
  abstract start(): void
  abstract pause(): void
  abstract resume(): void
  abstract destroy(): void

  protected createText(text: string, style?: Partial<TextStyle>): Text {
    const defaultStyle: TextStyle = {
      fontFamily: 'Arial',
      fontSize: 24,
      fill: 0xffffff,
      align: 'center'
    }
    return new Text(text, { ...defaultStyle, ...style })
  }

  protected createBackground(color: number, alpha: number = 1): Graphics {
    const bg = new Graphics()
    bg.beginFill(color, alpha)
    bg.drawRect(0, 0, this.app.screen.width, this.app.screen.height)
    bg.endFill()
    return bg
  }

  getEvents(): GameEvent[] {
    return this.events
  }

  clearEvents() {
    this.events = []
  }
}