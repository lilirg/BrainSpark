import { Text, Container, Graphics } from 'pixi.js'
import { BaseGame, type GameConfig, type GameEvent } from './BaseGame'

export interface NumberSpanConfig extends GameConfig {
  level?: 'easy' | 'medium' | 'hard'
  theme?: 'space' | 'ocean' | 'forest'
  ageGroup?: '5-6' | '7-8' | '9-11' | '12+'
}

export interface NumberSpanResult {
  type: 'NUMBER_SPAN'
  score: number
  maxLevel: number
  accuracy: number
  duration: number
  details: Array<{
    level: number
    sequence: string
    result: 'correct' | 'incorrect' | 'timeout'
  }>
}

type ThemeKey = 'space' | 'ocean' | 'forest'

const THEMES: Record<ThemeKey, { background: number; primary: number; secondary: number; text: number; accent: number }> = {
  space: {
    background: 0x0a0a2e,
    primary: 0x667eea,
    secondary: 0x764ba2,
    text: 0xffffff,
    accent: 0xffd700
  },
  ocean: {
    background: 0x006994,
    primary: 0x00b4d8,
    secondary: 0x0077b6,
    text: 0xffffff,
    accent: 0xffd700
  },
  forest: {
    background: 0x1a3c34,
    primary: 0x2d6a4f,
    secondary: 0x40916c,
    text: 0xffffff,
    accent: 0xffd700
  }
}

export class NumberSpanGame extends BaseGame {
  private sequenceDisplay: Container | null = null
  private inputContainer: Container | null = null
  private currentLevel = 0
  private currentSequence: number[] = []
  private userInput: number[] = []
  private results: Array<{ level: number; sequence: string; result: 'correct' | 'incorrect' | 'timeout' }> = []
  private isInputMode = false
  private gameStartTime = 0
  private config: NumberSpanConfig

  constructor(config: NumberSpanConfig) {
    super(config)
    this.config = config
  }

  async init(): Promise<void> {
    this.gameStartTime = Date.now()
    this.state.isRunning = true
    this.state.startTime = Date.now()
    await this.nextLevel()
  }

  start(): void {
    this.state.isRunning = true
    this.state.startTime = Date.now()
  }

  pause(): void {
    this.state.isPaused = true
  }

  resume(): void {
    this.state.isPaused = false
  }

  destroy(): void {
    this.state.isRunning = false
    this.state.isPaused = false
    this.app.destroy()
  }

  private getSequenceLength(level: number): number {
    const configMap = { easy: 3, medium: 4, hard: 5 }
    const levelKey = this.config.level || 'medium'
    const base = configMap[levelKey] ?? 4
    return base + Math.floor((level - 1) / 3)
  }

  private generateSequence(length: number): number[] {
    const seq: number[] = []
    for (let i = 0; i < length; i++) {
      seq.push(Math.floor(Math.random() * 9) + 1)
    }
    return seq
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => {
      const timer = setTimeout(resolve, ms)
      this.recordEvent('delay', { ms })
      // Store timer reference for cleanup
      ;(this as any)._tempTimer = timer
    })
  }

  private async nextLevel(): Promise<void> {
    if (this.state.isPaused) return

    this.currentLevel++
    this.userInput = []
    this.isInputMode = false

    const baseLength = this.getSequenceLength(this.currentLevel)
    this.currentSequence = this.generateSequence(baseLength)

    await this.showSequence()
  }

  private async showSequence(): Promise<void> {
    if (this.sequenceDisplay) {
      this.stage.removeChild(this.sequenceDisplay)
    }

    this.sequenceDisplay = new Container()
    const theme = THEMES[this.config.theme ?? 'space']

    const instructions = new Text('请记住以下数字', {
      fontSize: 28,
      fill: theme.text,
      fontFamily: 'Microsoft YaHei'
    })
    instructions.anchor.set(0.5, 0)
    instructions.x = this.config.width / 2
    instructions.y = 100
    this.sequenceDisplay.addChild(instructions)

    const sequenceText = new Text(
      '',
      {
        fontSize: 72,
        fill: theme.primary,
        fontFamily: 'Arial Black',
        fontWeight: 'bold'
      }
    )
    sequenceText.anchor.set(0.5, 0)
    sequenceText.x = this.config.width / 2
    sequenceText.y = 200
    this.sequenceDisplay.addChild(sequenceText)

    this.stage.addChild(this.sequenceDisplay)

    for (let i = 0; i < this.currentSequence.length; i++) {
      await this.delay(300)
      sequenceText.text = this.currentSequence[i].toString()
      sequenceText.tint = theme.accent
      await this.delay(600)
      sequenceText.tint = 0xffffff
    }

    await this.delay(500)
    sequenceText.text = '? ? ?'
    await this.delay(300)

    if (this.sequenceDisplay) {
      this.stage.removeChild(this.sequenceDisplay)
      this.sequenceDisplay = null
    }

    this.showInputPad()
  }

  private showInputPad(): void {
    this.isInputMode = true
    if (this.inputContainer) {
      this.stage.removeChild(this.inputContainer)
    }

    this.inputContainer = new Container()
    const theme = THEMES[this.config.theme ?? 'space']

    const instruction = new Text('请按顺序输入看到的数字', {
      fontSize: 20,
      fill: theme.text,
      fontFamily: 'Microsoft YaHei',
      align: 'center'
    })
    instruction.anchor.set(0.5, 0)
    instruction.x = this.config.width / 2
    instruction.y = 50
    this.inputContainer.addChild(instruction)

    const padX = this.config.width / 2 - 150
    const padY = 150

    for (let i = 0; i < 3; i++) {
      for (let j = 1; j <= 3; j++) {
        const num = i * 3 + j
        const btn = this.createNumberButton(num, theme)
        btn.x = padX + j * 100
        btn.y = padY + i * 80
        this.inputContainer.addChild(btn)
      }
    }

    const submitBtn = this.createSubmitButton(theme)
    submitBtn.x = padX + 200
    submitBtn.y = padY + 260
    this.inputContainer.addChild(submitBtn)

    const clearBtn = this.createClearButton(theme)
    clearBtn.x = padX
    clearBtn.y = padY + 260
    this.inputContainer.addChild(clearBtn)

    this.stage.addChild(this.inputContainer)
  }

  private createNumberButton(num: number, theme: Record<string, number>): Container {
    const container = new Container()
    const bg = new Graphics()
    bg.beginFill(theme.primary)
    bg.drawRect(0, 0, 80, 60)
    bg.endFill()
    container.addChild(bg)

    const text = new Text(num.toString(), {
      fontSize: 32,
      fill: theme.text,
      fontFamily: 'Arial Black',
      fontWeight: 'bold'
    })
    text.anchor.set(0.5)
    text.x = 40
    text.y = 30
    container.addChild(text)

    container.eventMode = 'static'
    container.cursor = 'pointer'
    container.on('pointerdown', () => {
      this.userInput.push(num)
      this.recordEvent('number_input', { num, index: this.userInput.length - 1 })
      
      const expected = this.currentSequence[this.userInput.length - 1]
      if (this.userInput[this.userInput.length - 1] !== expected) {
        this.finishLevel('incorrect')
        return
      }

      if (this.userInput.length === this.currentSequence.length) {
        this.finishLevel('correct')
      }
    })

    return container
  }

  private createSubmitButton(theme: Record<string, number>): Container {
    const container = new Container()
    const bg = new Graphics()
    bg.beginFill(0x52c41d)
    bg.drawRect(0, 0, 100, 50)
    bg.endFill()
    container.addChild(bg)

    const text = new Text('确认', {
      fontSize: 22,
      fill: theme.text,
      fontFamily: 'Microsoft YaHei',
      fontWeight: 'bold'
    })
    text.anchor.set(0.5)
    text.x = 50
    text.y = 25
    container.addChild(text)

    container.eventMode = 'static'
    container.cursor = 'pointer'
    container.on('pointerdown', () => {
      if (this.userInput.length > 0 && this.userInput.length < this.currentSequence.length) {
        this.finishLevel('timeout')
      }
    })

    return container
  }

  private createClearButton(theme: Record<string, number>): Container {
    const container = new Container()
    const bg = new Graphics()
    bg.beginFill(0xff4d4f)
    bg.drawRect(0, 0, 100, 50)
    bg.endFill()
    container.addChild(bg)

    const text = new Text('清除', {
      fontSize: 22,
      fill: theme.text,
      fontFamily: 'Microsoft YaHei',
      fontWeight: 'bold'
    })
    text.anchor.set(0.5)
    text.x = 50
    text.y = 25
    container.addChild(text)

    container.eventMode = 'static'
    container.cursor = 'pointer'
    container.on('pointerdown', () => {
      this.userInput = []
      this.recordEvent('clear_input', {})
    })

    return container
  }

  private finishLevel(result: 'correct' | 'incorrect' | 'timeout'): void {
    if (!this.inputContainer) return
    
    const sequenceStr = this.currentSequence.join('')
    this.results.push({
      level: this.currentLevel,
      sequence: sequenceStr,
      result
    })

    this.stage.removeChild(this.inputContainer)
    this.inputContainer = null
    this.isInputMode = false

    if (result === 'incorrect' || result === 'timeout') {
      this.showResult(result === 'incorrect' ? '答错了！' : '时间到！', this.currentSequence.join(''))
      setTimeout(() => {
        this.emitResult()
      }, 2000)
      return
    }

    setTimeout(() => {
      this.nextLevel()
    }, 800)
  }

  private showResult(title: string, subtitle?: string): void {
    if (this.sequenceDisplay) {
      this.stage.removeChild(this.sequenceDisplay)
    }

    this.sequenceDisplay = new Container()
    const theme = THEMES[this.config.theme ?? 'space']

    const titleText = new Text(title, {
      fontSize: 48,
      fill: theme.primary,
      fontFamily: 'Microsoft YaHei',
      fontWeight: 'bold'
    })
    titleText.anchor.set(0.5)
    titleText.x = this.config.width / 2
    titleText.y = 150
    this.sequenceDisplay.addChild(titleText)

    if (subtitle) {
      const subText = new Text(subtitle, {
        fontSize: 28,
        fill: theme.text,
        fontFamily: 'Microsoft YaHei'
      })
      subText.anchor.set(0.5)
      subText.x = this.config.width / 2
      subText.y = 220
      this.sequenceDisplay.addChild(subText)
    }

    this.stage.addChild(this.sequenceDisplay)
  }

  private emitResult(): void {
    const correctCount = this.results.filter(r => r.result === 'correct').length
    const total = this.results.length || 1
    const accuracy = Math.round((correctCount / total) * 100)
    const duration = Math.round((Date.now() - this.gameStartTime) / 1000)

    const result: NumberSpanResult = {
      type: 'NUMBER_SPAN',
      score: Math.min(100, Math.round(accuracy * 1.2)),
      maxLevel: this.currentLevel,
      accuracy,
      duration,
      details: this.results
    }

    this.recordEvent('game_complete', result)
    this.state.isRunning = false
  }
}