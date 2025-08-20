import React, { useEffect, useState } from 'react'
import { createSession } from '../api/client'
import { WorldsPanel } from './WorldsPanel'
import { GridPanel } from './GridPanel'

export function App() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [uiLog, setUiLog] = useState<string[]>([])
  const [worldName, setWorldName] = useState<string | null>(null)
  function log(msg: string) { setUiLog(prev => [...prev, msg]) }

  useEffect(() => {
    (async () => {
      try {
        log('Creating session…')
        const sid = await createSession()
        setSessionId(sid)
        log('Session ready: ' + sid)
      } catch (e: any) {
        log('Error creating session: ' + (e?.message || e))
      }
    })()
  }, [])
  async function copyLog() {
    try { await navigator.clipboard.writeText(uiLog.join('\n')) } catch {}
  }

  return (
    <div style={{ padding: 16, display: 'grid', gridTemplateColumns: '340px 1fr', gap: 16, height: '100vh', boxSizing: 'border-box', minWidth: 600, minHeight: 800 }}>
      {/* Left column: controls and log stacked, fills height */}
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0 }}>
        <div style={{ overflow: 'auto' }}>
          <WorldsPanel sessionId={sessionId} onLog={log} onWorldChange={(n) => setWorldName(n)} />
        </div>
        <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
          <h4 style={{ margin: 0 }}>UI Log</h4>
          <button onClick={copyLog}>Copy</button>
        </div>
        <div style={{ flex: 1, minHeight: 0 }}>
          <pre style={{ height: '100%', overflow: 'auto', background: '#111', color: '#ddd', padding: 8, userSelect: 'text', whiteSpace: 'pre-wrap', borderRadius: 4 }}>
            {uiLog.join('\n')}
          </pre>
        </div>
      </div>
      {/* Right column: grid fills and centers */}
      <div style={{ minWidth: 0, height: '100%' }}>
        <GridPanel sessionId={sessionId} worldName={worldName} onLog={log} />
      </div>
    </div>
  )
}
