import { Text, Container, Graphics, Sprite, Texture } from 'pixi.js'
import { BaseGame, type GameConfig, type GameEvent } from './BaseGame'

export interface PatternConfig extends GameConfig {
  gridSize?: number
  timeLimit?: number
  theme?: 'space' | 'ocean' | 'forest'
  difficulty?: 'easy' | 'medium' | 'hard'
}

export interface PatternResult {
  type: 'PATTERN_RECOGNITION'
  score: number
  maxRound: number
  accuracy: number
  duration: number
  details: Array<{
    round: number
    correct: boolean
    time: number
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

const SHAPES = ['⭐', '🔷', '🔶', '🔺', '🔻', '💎', '🌟', '⬛', '⬜', '🔵', '🟢', '🟡', '🔴', '🟣']

export class PatternRecognitionGame extends BaseGame {
  private config: PatternConfig
  private stageDisplay: Container | null = null
  private currentRound = 0
  private currentPattern: string[] = []
  private currentDisplay: string[] = []
  private selectedIndices: Set<number> = new Set()
  private results: Array<{ round: number; correct: boolean; time: number }> = []
  private gameStartTime = 0
  private roundStartTime = 0
  private timerHandle: number | null = null
  private timeLimit = 30
  private totalRounds = 5

  constructor(config: PatternConfig) {
    super(config)
    this.config = config
    this.timeLimit = config.timeLimit ?? 30
    this.totalRounds = config.gridSize ? Math.min(5, Math.floor(config.gridSize / 2)) : 5
  }

  async init(): Promise<void> {
    this.gameStartTime = Date.now()
    this.state.isRunning = true
    this.state.startTime = Date.now()
    this.timeLimit = this.config.timeLimit ?? 30
    await this.nextRound()
  }

  start(): void {
    this.state.isRunning = true
    this.state.startTime = Date.now()
  }

  pause(): void {
    this.state.isPaused = true
    if (this.timerHandle) {
      cancelAnimationFrame(this.timerHandle)
      this.timerHandle = null
    }
  }

  resume(): void {
    this.state.isPaused = false
  }

  destroy(): void {
    this.state.isRunning = false
    this.state.isPaused = false
    this.app.destroy()
    if (this.timerHandle) {
      cancelAnimationFrame(this.timerHandle)
      this.timerHandle = null
    }
  }

  private getGridSize(): number {
    switch (this.config.difficulty) {
      case 'easy': return 3
      case 'hard': return 4
      default: return 3
    }
  }

  private getPatternLength(): number {
    switch (this.config.difficulty) {
      case 'easy': return 3
      case 'hard': return 5
      default: return 4
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => {
      const timer = setTimeout(resolve, ms)
      this.recordEvent('delay', { ms })
      ;(this as any)._tempTimer = timer
    })
  }

  private async nextRound(): Promise<void> {
    if (this.state.isPaused) return

    this.currentRound++
    this.selectedIndices.clear()

    if (this.currentRound > this.totalRounds) {
      this.emitResult()
      return
    }

    const gridSize = this.getGridSize()
    const totalCells = gridSize * gridSize
    const patternLength = Math.min(this.getPatternLength(), totalCells - 2)

    // Generate random pattern
    const indices = Array.from({ length: totalCells }, (_, i) => i)
    for (let i = indices.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      ;[indices[i], indices[j]] = [indices[j], indices[i]]
    }
    this.currentPattern = indices.slice(0, patternLength).map(i => SHAPES[i % SHAPES.length])
    this.currentDisplay = Array(totalCells).fill('')

    await this.showPattern()
  }

  private async showPattern(): Promise<void> {
    if (this.stageDisplay) {
      this.stageDisplay = null
    }

    const gridSize = this.getGridSize()
    const cellSize = Math.min(80, Math.floor(Math.min(this.config.width, 500) / gridSize))
    const offsetX = (this.config.width - cellSize * gridSize) / 2
    const offsetY = 100

    this.stageDisplay = new Container()
    const theme = THEMES[this.config.theme ?? 'space']

    const title = new Text('记住这些图案！', {
      fontSize: 28,
      fill: theme.text,
      fontFamily: 'Microsoft YaHei'
    })
    title.anchor.set(0.5, 0)
    title.x = this.config.width / 2
    title.y = 30
    this.stageDisplay.addChild(title)

    // Draw grid
    for (let row = 0; row < gridSize; row++) {
      for (let col = 0; col < gridSize; col++) {
        const idx = row * gridSize + col
        const cell = new Container()
        const bg = new Graphics()
        bg.beginFill(0x2a2a4a)
        bg.drawRect(0, 0, cellSize, cellSize)
        bg.endFill()
        bg.beginFill(0x3a3a5a)
        bg.drawRect(2, 2, cellSize - 4, cellSize - 4)
        bg.endFill()
        cell.addChild(bg)

        const shapeText = new Text('', {
          fontSize: cellSize * 0.5,
          align: 'center'
        })
        shapeText.anchor.set(0.5)
        shapeText.x = cellSize / 2
        shapeText.y = cellSize / 2
        cell.addChild(shapeText)

        cell.x = offsetX + col * cellSize
        cell.y = offsetY + row * cellSize

        if (this.currentDisplay[idx]) {
          shapeText.text = this.currentDisplay[idx]
        }

        this.stageDisplay!.addChild(cell)
      }
    }

    this.stage.addChild(this.stageDisplay!)

    // Show pattern
    for (let i = 0; i < this.currentPattern.length; i++) {
      await this.delay(200)
      const idx = this.currentPattern.indexOf(this.currentPattern[i])
      const cell = this.stageDisplay!.children[idx] as Container
      if (cell && cell.children[1]) {
        const shapeText = cell.children[1] as Text
        shapeText.tint = theme.accent
        await this.delay(500)
        shapeText.tint = 0xffffff
      }
    }

    await this.delay(500)

    // Clear and start input
    if (this.stageDisplay) {
      for (const child of this.stageDisplay.children) {
        if (child instanceof Container && child.children[1]) {
          const shapeText = child.children[1] as Text
          shapeText.text = ''
          shapeText.tint = 0xffffff
        }
      }
    }

    this.showInputGrid()
  }

  private showInputGrid(): void {
    if (this.stageDisplay) {
      this.stageDisplay = null
    }

    const gridSize = this.getGridSize()
    const cellSize = Math.min(80, Math.floor(Math.min(this.config.width, 500) / gridSize))
    const offsetX = (this.config.width - cellSize * gridSize) / 2
    const offsetY = 100

    this.stageDisplay = new Container()
    const theme = THEMES[this.config.theme ?? 'space']

    const title = new Text('选择刚才看到的图案！', {
      fontSize: 24,
      fill: theme.text,
      fontFamily: 'Microsoft YaHei'
    })
    title.anchor.set(0.5, 0)
    title.x = this.config.width / 2
    title.y = 30
    this.stageDisplay.addChild(title)

    // Timer
    const timerText = new Text(this.timeLimit.toString(), {
      fontSize: 32,
      fill: theme.accent,
      fontFamily: 'Arial Black'
    })
    timerText.anchor.set(0.5)
    timerText.x = this.config.width / 2
    timerText.y = 70
    this.stageDisplay.addChild(timerText)

    // Draw grid
    for (let row = 0; row < gridSize; row++) {
      for (let col = 0; col < gridSize; col++) {
        const idx = row * gridSize + col
        const cell = new Container()
        const bg = new Graphics()
        bg.beginFill(0x2a2a4a)
        bg.drawRect(0, 0, cellSize, cellSize)
        bg.endFill()
        bg.beginFill(0x3a3a5a)
        bg.drawRect(2, 2, cellSize - 4, cellSize - 4)
        bg.endFill()
        cell.addChild(bg)

        const shapeText = new Text('', {
          fontSize: cellSize * 0.5,
          align: 'center'
        })
        shapeText.anchor.set(0.5)
        shapeText.x = cellSize / 2
        shapeText.y = cellSize / 2
        cell.addChild(shapeText)

        cell.x = offsetX + col * cellSize
        cell.y = offsetY + row * cellSize
        cell.eventMode = 'static'
        cell.cursor = 'pointer'

        cell.on('pointerdown', () => {
          if (this.selectedIndices.has(idx)) {
            this.selectedIndices.delete(idx)
            shapeText.text = ''
            bg.beginFill(0x2a2a4a)
            bg.drawRect(0, 0, cellSize, cellSize)
            bg.endFill()
          } else {
            this.selectedIndices.add(idx)
            shapeText.text = SHAPES[idx % SHAPES.length]
            bg.beginFill(theme.primary)
            bg.drawRect(0, 0, cellSize, cellSize)
            bg.endFill()
          }
          this.recordEvent('pattern_select', { idx, selected: this.selectedIndices.size })
        })

        this.stageDisplay!.addChild(cell)
      }
    }

    // Submit button
    const submitBtn = new Container()
    const submitBg = new Graphics()
    submitBg.beginFill(0x52c41d)
    submitBg.drawRect(0, 0, 120, 50)
    submitBg.endFill()
    submitBtn.addChild(submitBg)

    const submitText = new Text('确认', {
      fontSize: 22,
      fill: theme.text,
      fontFamily: 'Microsoft YaHei',
      fontWeight: 'bold'
    })
    submitText.anchor.set(0.5)
    submitText.x = 60
    submitText.y = 25
    submitBtn.addChild(submitText)

    submitBtn.x = this.config.width / 2 - 60
    submitBtn.y = offsetY + gridSize * cellSize + 30
    submitBtn.eventMode = 'static'
    submitBtn.cursor = 'pointer'

    submitBtn.on('pointerdown', () => {
      this.checkAnswer(timerText)
    })

    this.stageDisplay!.addChild(submitBtn)

    // Start timer
    this.roundStartTime = Date.now()
    this.startTimer(timerText, theme)

    this.stage.addChild(this.stageDisplay!)
  }

  private startTimer(timerText: Text, theme: Record<string, number>): void {
    let remaining = this.timeLimit
    const updateTimer = () => {
      if (this.state.isPaused) {
        this.timerHandle = requestAnimationFrame(updateTimer)
        return
      }
      remaining--
      timerText.text = remaining.toString()
      if (remaining <= 5) {
        timerText.tint = 0xff0000
      }
      if (remaining <= 0) {
        this.checkAnswer(timerText)
        return
      }
      this.timerHandle = requestAnimationFrame(updateTimer)
    }
    this.timerHandle = requestAnimationFrame(updateTimer)
  }

  private checkAnswer(timerText: Text): void {
    if (this.timerHandle) {
      cancelAnimationFrame(this.timerHandle)
      this.timerHandle = null
    }

    const elapsed = Date.now() - this.roundStartTime
    const correct = this.checkPattern()
    this.results.push({
      round: this.currentRound,
      correct,
      time: elapsed
    })

    this.recordEvent('pattern_check', { correct, selected: this.selectedIndices.size })

    // Show result
    const resultText = new Text(correct ? '正确！' : '错误！', {
      fontSize: 48,
      fill: correct ? 0x52c41d : 0xff4d4f,
      fontFamily: 'Microsoft YaHei',
      fontWeight: 'bold'
    })
    resultText.anchor.set(0.5)
    resultText.x = this.config.width / 2
    resultText.y = this.config.height / 2
    if (this.stageDisplay) {
      this.stageDisplay.addChild(resultText)
    }

    setTimeout(() => {
      this.nextRound()
    }, 1000)
  }

  private checkPattern(): boolean {
    if (this.selectedIndices.size !== this.currentPattern.length) return false
    
    const selectedArr = Array.from(this.selectedIndices)
    for (let i = 0; i < this.currentPattern.length; i++) {
      if (!this.selectedIndices.has(i)) return false
    }
    return true
  }

  private emitResult(): void {
    const correctCount = this.results.filter(r => r.correct).length
    const total = this.results.length || 1
    const accuracy = Math.round((correctCount / total) * 100)
    const duration = Math.round((Date.now() - this.gameStartTime) / 1000)

    const avgTime = Math.round(this.results.reduce((sum, r) => sum + r.time, 0) / this.results.length / 1000)

    const result: PatternResult = {
      type: 'PATTERN_RECOGNITION',
      score: Math.min(100, Math.round(accuracy * 1.1)),
      maxRound: this.currentRound,
      accuracy,
      duration,
      details: this.results
    }

    this.recordEvent('game_complete', result)
    this.state.isRunning = false
  }
}