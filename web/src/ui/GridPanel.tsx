import React, { useEffect, useMemo, useRef, useState } from 'react'
import { cellsCurrent, cellsSet, listWorlds } from '../api/client'

type Cell = [number, number, string, number | null]

export function GridPanel({ sessionId, worldName, onLog }: { sessionId: string | null; worldName: string | null; onLog: (msg: string) => void }) {
  const [cells, setCells] = useState<Cell[]>([])
  const [radius, setRadius] = useState<number>(10)
  const [hover, setHover] = useState<{ q: number; r: number } | null>(null)
  const wrapRef = useRef<HTMLDivElement | null>(null)
  const [dims, setDims] = useState<{ w: number; h: number }>({ w: 0, h: 0 })

  useEffect(() => {
    const el = wrapRef.current
    if (!el) return
    const obs = new ResizeObserver((entries) => {
      for (const e of entries) {
        const cr = e.contentRect
        setDims({ w: cr.width, h: cr.height })
      }
    })
    obs.observe(el)
    return () => obs.disconnect()
  }, [])

  useEffect(() => {
    (async () => {
      if (!sessionId || !worldName) { setCells([]); return }
      try {
        onLog(`Loading world ${worldName} metadata…`)
        const ws = await listWorlds(sessionId)
        const meta = ws.find(w => w.name === worldName)
        if (meta) setRadius(meta.radius)
                onLog(`Loading cells for ${worldName}…`)
        const currentCells = await cellsCurrent(sessionId)
        setCells(currentCells)
        onLog(`Loaded ${currentCells.length} active cells`)
      } catch (e: any) {
        onLog('Error loading cells: ' + (e?.message || e))
      }
    })()
  }, [sessionId, worldName])

  const cellMap = useMemo(() => new Map<string, Cell>(cells.map(c => [`${c[0]},${c[1]}`, c])), [cells])

  const hexSize = 14
  const S = hexSize
  // Compute tight grid bounds and add padding so strokes never touch container edges
  const R = Math.max(1, Math.floor(radius))
  const GRID_W = 2 * Math.sqrt(3) * S * (R + 0.5)
  const GRID_H = 3 * S * R + 2 * S
  const PAD = S * 1.0
  const VIEW_W = GRID_W + 2 * PAD
  const VIEW_H = GRID_H + 2 * PAD
  const centerX = VIEW_W / 2, centerY = VIEW_H / 2

  function axialToPixel(q: number, r: number) {
  const x = S * (Math.sqrt(3) * q + (Math.sqrt(3) / 2) * r)
  const y = S * (1.5 * r)
  return [x + centerX, y + centerY]
  }

  function cycleState(s: string): string {
    const order = ['_', 'x']
    const i = order.indexOf(s)
    return order[(i + 1) % order.length]
  }

  function pickCellFromEvent(ev: React.MouseEvent<SVGSVGElement, MouseEvent>): { q: number; r: number } | null {
    const svg = ev.currentTarget
    const rect = svg.getBoundingClientRect()
    // Map mouse position in CSS pixels to viewBox coords accounting for preserveAspectRatio="xMidYMid meet"
    const cx = ev.clientX - rect.left
    const cy = ev.clientY - rect.top
  const scale = Math.min(rect.width / VIEW_W, rect.height / VIEW_H)
    const contentW = VIEW_W * scale
    const contentH = VIEW_H * scale
    const offsetX = (rect.width - contentW) / 2
    const offsetY = (rect.height - contentH) / 2
    // If pointer outside the rendered content area, no selection
    if (cx < offsetX || cx > offsetX + contentW || cy < offsetY || cy > offsetY + contentH) return null
    const px = (cx - offsetX) / scale
    const py = (cy - offsetY) / scale
    // Convert to axial coordinates (pointy-top) relative to center, then round to nearest hex
    const x = px - centerX
    const y = py - centerY
    const qf = (Math.sqrt(3) / 3 * x - 1 / 3 * y) / S
    const rf = (2 / 3 * y) / S
    // Cube rounding
    let xf = qf, yf = rf, zf = -qf - rf
    let xi = Math.round(xf), yi = Math.round(yf), zi = Math.round(zf)
    const dx = Math.abs(xi - xf), dy = Math.abs(yi - yf), dz = Math.abs(zi - zf)
    if (dx > dy && dx > dz) {
      xi = -yi - zi
    } else if (dy > dz) {
      yi = -xi - zi
    } else {
      zi = -xi - yi
    }
    const q = xi
    const r = yi
  const R = Math.max(2, Math.floor(radius))
    if (Math.abs(q) > R || Math.abs(r) > R || Math.abs(q + r) > R) return null
    return { q, r }
  }

  async function onCanvasClick(ev: React.MouseEvent<SVGSVGElement, MouseEvent>) {
    if (!sessionId) return
    const picked = pickCellFromEvent(ev)
    if (!picked) return
    const key = `${picked.q},${picked.r}`
    const cur = cellMap.get(key) || [picked.q, picked.r, '_', null]
    const nextState = cycleState(cur[2])
    try {
      await cellsSet(sessionId, picked.q, picked.r, nextState, cur[3])
      const updated = new Map(cellMap)
      updated.set(key, [picked.q, picked.r, nextState, cur[3]])
      setCells(Array.from(updated.values()))
    } catch (e: any) {
      onLog('Error setting cell: ' + (e?.message || e))
    }
  }

  function onCanvasMove(ev: React.MouseEvent<SVGSVGElement, MouseEvent>) {
    const picked = pickCellFromEvent(ev)
    if (!picked) {
      if (hover) setHover(null)
      return
    }
    if (!hover || hover.q !== picked.q || hover.r !== picked.r) setHover(picked)
  }

  function onCanvasLeave() {
    setHover(null)
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      <h3 style={{ margin: '0 0 8px 0' }}>World</h3>
      <div ref={wrapRef} style={{ flex: 1, minHeight: 0, border: '1px solid #ccc', borderRadius: 4, overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        {(() => {
          const side = Math.max(10, Math.floor(Math.min(dims.w || 0, dims.h || 0)))
          return (
        <svg
          viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
          width={side}
          height={side}
          preserveAspectRatio="xMidYMid meet"
          style={{ background: '#fff', display: 'block', cursor: 'pointer' }}
          onMouseDown={onCanvasClick}
          onMouseMove={onCanvasMove}
          onMouseLeave={onCanvasLeave}
        >
        {Array.from({ length: radius * 2 + 1 }).map((_, rq) =>
          Array.from({ length: radius * 2 + 1 }).map((__, rr) => {
            const q = rq - radius, r = rr - radius
            if (Math.abs(q + r) > radius) return null
            const [x, y] = axialToPixel(q, r)
            const poly = Array.from({ length: 6 }).map((__, i) => {
              const a = Math.PI / 3 * i + Math.PI / 6
              const px = x + S * Math.cos(a)
              const py = y + S * Math.sin(a)
              return `${px},${py}`
            }).join(' ')
            const key = `${q},${r}`
            const c = cellMap.get(key)
            const state = c ? c[2] : '_'
            const fill = state === '_' ? '#222' : '#e66'
            const isHover = hover && hover.q === q && hover.r === r
            return <polygon key={key} points={poly} fill={fill} stroke={isHover ? '#ffd54a' : '#444'} strokeWidth={isHover ? 2 : 1} vectorEffect="non-scaling-stroke" />
          })
        )}
        </svg>
          )
        })()}
      </div>
    </div>
  )
}
