import React, { useEffect, useRef, useState } from 'react'
import { getTuiFrame } from '../api/client'

export function PreTUI({ sessionId }: { sessionId: string | null }) {
  const [frame, setFrame] = useState<string>('')
  const timer = useRef<number | null>(null)

  useEffect(() => {
    const stop = () => { if (timer.current) { window.clearInterval(timer.current); timer.current = null } }
    const start = () => {
      if (!sessionId) return
      stop()
      const tick = async () => {
        try { setFrame(await getTuiFrame(sessionId, 80, 24)) } catch { /* ignore */ }
      }
      tick()
      timer.current = window.setInterval(tick, 500)
    }
    start()
    return stop
  }, [sessionId])

  return (
    <div style={{ height: '100%', width: '100%', overflow: 'auto', background: '#111', color: '#ddd', border: '1px solid #333' }}>
      <pre style={{ margin: 0, fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace', fontSize: 12, lineHeight: '14px', padding: 8 }}>
        {frame}
      </pre>
    </div>
  )
}
