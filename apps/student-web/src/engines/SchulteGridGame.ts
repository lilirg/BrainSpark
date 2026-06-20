import { Container, Graphics, Text, TextStyle } from 'pixi.js'
import { BaseGame, type GameConfig } from './BaseGame'
import { MicroTimer } from './MicroTimer'

interface GridCell {
  value: number
  graphics: Graphics
  text: Text
  row: number
  col: number
}

export interface SchulteConfig extends GameConfig {
  gridSize?: number
  theme?: 'space' | 'ocean' | 'forest'
  ageGroup?: '6-8' | '9-11' | '12+'
}

const THEMES = {
  space: { bg: 0x0a0a2e, cell: 0x16213e, hover: 0x0f3460, text: 0xe94560, accent: 0x533483 },
  ocean: { bg: 0x006994, cell: 0x0077b6, hover: 0x0096c7, text: 0xcaf0f8, accent: 0x48cae4 },
  forest: { bg: 0x1b4332, cell: 0x2d6a4f, hover: 0x40916c, text: 0xd8f3dc, accent: 0x52b788 }
}

export class SchulteGridGame extends BaseGame {
  private gridSize: number
  private cells: GridCell[] = []
  private currentNumber: number = 1
  private totalNumbers: number
  private timer: MicroTimer
  private theme: typeof THEMES[keyof typeof THEMES]
  private ageGroup: string
  private gridContainer: Container
  private infoText: Text
  private scoreText: Text
  private isComplete: boolean = false

  constructor(config: SchulteConfig) {
    super(config)
    this.gridSize = config.gridSize || 5
    this.totalNumbers = this.gridSize * this.gridSize
    this.timer = new MicroTimer()
    this.theme = THEMES[config.theme || 'space']
    this.ageGroup = config.ageGroup || '9-11'
    this.gridContainer = new Container()
    this.infoText = this.createText('', { fontSize: 20, fill: this.theme.text })
    this.scoreText = this.createText('', { fontSize: 18, fill: this.theme.accent })
  }

  async init(): Promise<void> {
    // 添加背景
    this.stage.addChild(this.createBackground(this.theme.bg))

    // 添加标题
    const title = this.createText('舒尔特方格', {
      fontSize: 32,
      fill: this.theme.text,
      fontWeight: 'bold'
    })
    title.x = (this.app.screen.width - title.width) / 2
    title.y = 20
    this.stage.addChild(title)

    // 添加信息文本
    this.infoText.text = `请按顺序点击 1 到 ${this.totalNumbers}`
    this.infoText.x = (this.app.screen.width - this.infoText.width) / 2
    this.infoText.y = 70
    this.stage.addChild(this.infoText)

    // 添加分数文本
    this.scoreText.text = '用时: 0.00s'
    this.scoreText.x = (this.app.screen.width - this.scoreText.width) / 2
    this.scoreText.y = 100
    this.stage.addChild(this.scoreText)

    // 创建网格
    this.createGrid()

    // 添加网格到舞台
    this.stage.addChild(this.gridContainer)
  }

  private createGrid() {
    const padding = 40
    const topOffset = 140
    const cellSize = Math.min(
      (this.app.screen.width - padding * 2) / this.gridSize,
      (this.app.screen.height - topOffset - padding) / this.gridSize
    )
    const gridWidth = cellSize * this.gridSize
    const startX = (this.app.screen.width - gridWidth) / 2
    const startY = topOffset + (this.app.screen.height - topOffset - gridWidth) / 2

    // 生成随机数字序列
    const numbers = this.generateShuffledNumbers()

    let index = 0
    for (let row = 0; row < this.gridSize; row++) {
      for (let col = 0; col < this.gridSize; col++) {
        const x = startX + col * cellSize
        const y = startY + row * cellSize
        const value = numbers[index]

        const cell = new Graphics()
        cell.beginFill(this.theme.cell)
        cell.drawRoundedRect(0, 0, cellSize - 4, cellSize - 4, 8)
        cell.endFill()
        cell.x = x + 2
        cell.y = y + 2
        cell.eventMode = 'static'
        cell.cursor = 'pointer'

        const text = new Text(value.toString(), {
          fontSize: Math.floor(cellSize * 0.4),
          fill: this.theme.text,
          fontWeight: 'bold'
        } as TextStyle)
        text.x = cell.x + (cellSize - 4 - text.width) / 2
        text.y = cell.y + (cellSize - 4 - text.height) / 2

        cell.on('pointerdown', () => this.handleCellClick(value, cell, text))
        cell.on('pointerover', () => {
          if (!cell.destroyed) {
            cell.tint = 0xcccccc
          }
        })
        cell.on('pointerout', () => {
          if (!cell.destroyed) {
            cell.tint = 0xffffff
          }
        })

        this.gridContainer.addChild(cell)
        this.gridContainer.addChild(text)

        this.cells.push({ value, graphics: cell, text, row, col })
        index++
      }
    }
  }

  private generateShuffledNumbers(): number[] {
    const numbers = Array.from({ length: this.totalNumbers }, (_, i) => i + 1)
    for (let i = numbers.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [numbers[i], numbers[j]] = [numbers[j], numbers[i]]
    }
    return numbers
  }

  private handleCellClick(value: number, cell: Graphics, text: Text) {
    if (this.isComplete) return

    if (value === this.currentNumber) {
      // 正确点击
      this.recordEvent('correct_click', { value, currentNumber: this.currentNumber })

      // 标记为已找到
      cell.beginFill(this.theme.accent)
      cell.drawRoundedRect(0, 0, cell.width, cell.height, 8)
      cell.endFill()
      cell.eventMode = 'none'
      cell.cursor = 'default'

      this.currentNumber++

      if (this.currentNumber > this.totalNumbers) {
        this.completeGame()
      }
    } else {
      // 错误点击
      this.recordEvent('wrong_click', { value, currentNumber: this.currentNumber })

      // 闪烁红色提示
      const originalColor = this.theme.cell
      cell.tint = 0xff0000
      setTimeout(() => {
        if (!cell.destroyed) cell.tint = 0xffffff
      }, 200)
    }
  }

  private completeGame() {
    this.isComplete = true
    const elapsed = this.timer.stop()
    this.state.score = Math.max(0, Math.round(1000 - elapsed / 1000))

    this.recordEvent('game_complete', {
      elapsed,
      score: this.state.score,
      gridSize: this.gridSize
    })

    this.infoText.text = '恭喜完成！'
    this.infoText.style.fill = '#00ff00'

    // 显示完成动画
    const completeText = this.createText('🎉', { fontSize: 64 })
    completeText.x = (this.app.screen.width - completeText.width) / 2
    completeText.y = this.app.screen.height / 2 - 50
    this.stage.addChild(completeText)
  }

  start(): void {
    this.state.isRunning = true
    this.state.startTime = Date.now()
    this.timer.start()
    this.recordEvent('game_start', { gridSize: this.gridSize })
  }

  pause(): void {
    this.state.isPaused = true
    this.timer.pause()
    this.recordEvent('game_pause')
  }

  resume(): void {
    this.state.isPaused = false
    this.timer.resume()
    this.recordEvent('game_resume')
  }

  destroy(): void {
    this.timer.reset()
    this.cells = []
    this.app.destroy(true)
  }

  updateScore() {
    const elapsed = this.timer.getMilliseconds()
    this.scoreText.text = `用时: ${(elapsed / 1000).toFixed(2)}s`
  }
}