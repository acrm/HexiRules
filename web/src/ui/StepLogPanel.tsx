import React from 'react'

type Props = {
  logs: string[]
  onClear: () => void
}

export function StepLogPanel({ logs, onClear }: Props) {
  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 6, flexShrink: 0 }}>
        <button onClick={onClear} style={{ fontSize: '11px', padding: '3px 6px' }}>Clear</button>
      </div>
      <div style={{ flex: 1, minHeight: 0 }}>
        <pre style={{ height: '100%', overflow: 'auto', background: '#111', color: '#ddd', padding: 6, userSelect: 'text', whiteSpace: 'pre-wrap', borderRadius: 4, margin: 0, fontSize: '10px', border: '1px solid #ccc' }}>
          {logs.length > 0 ? logs.join('\n') : '(no step logs)'}
        </pre>
      </div>
    </div>
  )
}
