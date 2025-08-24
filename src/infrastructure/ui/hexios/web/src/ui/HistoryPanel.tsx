import React, { useEffect, useState } from 'react'
import { listHistory, go, next_, prev } from '../api/client'

type Props = {
  sessionId: string | null
  onSelectIndex?: (index: number) => void
  refreshTrigger?: number
  onProgress?: () => Promise<void>
}

export function HistoryPanel({ sessionId, onSelectIndex, refreshTrigger, onProgress }: Props) {
  const [items, setItems] = useState<{ index: number; active_count: number }[]>([])
  const [busy, setBusy] = useState(false)

  async function refresh() {
    if (!sessionId) return
    try {
      setBusy(true)
      const it = await listHistory(sessionId)
      setItems(it)
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => { refresh() }, [sessionId])

  // Auto-refresh when trigger changes (after step or world switch)
  useEffect(() => {
    if (refreshTrigger !== undefined && refreshTrigger > 0) {
      refresh()
    }
  }, [refreshTrigger])

  async function doPrev() { if (!sessionId) return; await prev(sessionId); await refresh() }
  async function doNext() { if (!sessionId) return; await next_(sessionId); await refresh() }
  async function select(i: number) { if (!sessionId) return; await go(sessionId, i); onSelectIndex?.(i); await refresh() }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', gap: 4, alignItems: 'center', marginBottom: 8, flexShrink: 0, flexWrap: 'wrap' }}>
        <button onClick={doPrev} disabled={!sessionId || busy} style={{ fontSize: '12px', padding: '4px 8px' }}>Prev</button>
        <button onClick={doNext} disabled={!sessionId || busy} style={{ fontSize: '12px', padding: '4px 8px' }}>Next</button>
        <button onClick={refresh} disabled={!sessionId || busy} style={{ fontSize: '12px', padding: '4px 8px' }}>Refresh</button>
        {onProgress && (
          <button onClick={onProgress} disabled={!sessionId || busy} style={{ fontSize: '12px', padding: '4px 8px', backgroundColor: '#007acc', color: 'white', border: 'none', borderRadius: 3 }}>Progress</button>
        )}
      </div>
      <div style={{ border: '1px solid #ddd', borderRadius: 4, overflow: 'auto', flex: 1, minHeight: 0 }}>
        {items.map(it => (
          <div key={it.index} onClick={() => select(it.index)} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 8px', cursor: 'pointer', borderBottom: '1px solid #eee', fontSize: '12px' }}>
            <span>#{it.index}</span>
            <span style={{ color: '#666' }}>{it.active_count} cells</span>
          </div>
        ))}
        {items.length === 0 && <div style={{ padding: 8, color: '#888', fontSize: '12px' }}>(empty)</div>}
      </div>
    </div>
  )
}
