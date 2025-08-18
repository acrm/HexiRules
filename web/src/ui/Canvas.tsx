import React, { useEffect, useRef } from 'react'
import type { Cell } from '../api/client'

function axialToPixel(q: number, r: number, size: number): { x: number; y: number } {
  // Simple axial to pixel for pointy-top hexes (approx)
  const x = size * (Math.sqrt(3) * q + (Math.sqrt(3) / 2) * r)
  const y = size * (1.5 * r)
  return { x, y }
}

export function Canvas({ cells, width = 600, height = 400 }: { cells: Cell[]; width?: number; height?: number }) {
  const ref = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    const c = ref.current
    if (!c) return
    const ctx = c.getContext('2d')!
    ctx.clearRect(0, 0, c.width, c.height)

    // center
    ctx.save()
    ctx.translate(c.width / 2, c.height / 2)

    const size = 8
    for (const [q, r, state, dir] of cells) {
      if (state === '_') continue
      const { x, y } = axialToPixel(q, r, size)
      // draw as small circle for now
      ctx.beginPath()
      ctx.arc(x, y, size * 0.6, 0, Math.PI * 2)
      ctx.fillStyle = '#58a6ff'
      ctx.fill()
      // direction marker
      if (dir && dir >= 1 && dir <= 6) {
        ctx.beginPath()
        ctx.moveTo(x, y)
        const angle = ((dir - 1) * 60 * Math.PI) / 180
        ctx.lineTo(x + Math.cos(angle) * size, y + Math.sin(angle) * size)
        ctx.strokeStyle = '#ffd700'
        ctx.lineWidth = 1.5
        ctx.stroke()
      }
    }

    ctx.restore()
  }, [cells])

  return <canvas ref={ref} width={width} height={height} style={{ border: '1px solid #ccc', background: '#fff' }} />
}
