import React, { useEffect, useState } from 'react'
import { createSession, createWorld, listHistory, getLogs, step, go, prev, next_ } from '../api/client'

export function App() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [rules, setRules] = useState<string>('')
  const [history, setHistory] = useState<{ index: number; active_count: number }[]>([])
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null)
  const [logs, setLogs] = useState<string[]>([])
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    (async () => {
      const sid = await createSession()
      setSessionId(sid)
      await createWorld(sid, 'World', 20, '')
      const h = await listHistory(sid)
      setHistory(h)
      const sel = h.length ? h[h.length - 1].index : null
      setSelectedIndex(sel)
      if (sel !== null) setLogs(await getLogs(sid, sel))
    })()
  }, [])

  async function refresh() {
    if (!sessionId) return
    const h = await listHistory(sessionId)
    setHistory(h)
    const sel = h.length ? h[h.length - 1].index : null
    setSelectedIndex(sel)
    if (sel !== null) setLogs(await getLogs(sessionId, sel))
  }

  async function doStep() {
    if (!sessionId) return
    setBusy(true)
    try {
      await step(sessionId, rules || undefined)
      await refresh()
    } finally {
      setBusy(false)
    }
  }

  async function select(i: number) {
    if (!sessionId) return
    await go(sessionId, i)
    setSelectedIndex(i)
    setLogs(await getLogs(sessionId, i))
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 16, padding: 16 }}>
      <div>
        <h3>Rules</h3>
        <textarea style={{ width: '100%', height: 120 }} value={rules} onChange={e => setRules(e.target.value)} />
        <div style={{ marginTop: 8 }}>
          <button onClick={doStep} disabled={busy}>{busy ? 'Progress…' : 'Progress'}</button>
          <button onClick={() => sessionId && prev(sessionId).then(refresh)} style={{ marginLeft: 8 }}>Prev</button>
          <button onClick={() => sessionId && next_(sessionId).then(refresh)} style={{ marginLeft: 8 }}>Next</button>
        </div>
        <h3 style={{ marginTop: 16 }}>History</h3>
        <ul style={{ listStyle: 'none', padding: 0, maxHeight: 200, overflow: 'auto', border: '1px solid #ccc' }}>
          {history.map(h => (
            <li key={h.index} style={{ padding: 4, cursor: 'pointer', background: selectedIndex === h.index ? '#eef' : 'transparent' }} onClick={() => select(h.index)}>
              Step {h.index} — active {h.active_count}
            </li>
          ))}
        </ul>
      </div>
      <div>
        <h3>Step Logs</h3>
        <pre style={{ height: 360, overflow: 'auto', background: '#111', color: '#ddd', padding: 12 }}>{logs.join('\n')}</pre>
        <div style={{ marginTop: 12, opacity: 0.6 }}>Canvas placeholder — implement hex rendering next.</div>
      </div>
    </div>
  )
}
