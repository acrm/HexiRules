import React, { useEffect, useState } from 'react'

type Props = {
  sessionId: string | null
  rulesText: string
  onRulesChange: (text: string) => void
}

const PRESETS: { key: string; name: string; text: string }[] = [
  {
    key: 'tree_apple',
    name: 'Tree & Apple',
    text: [
      't[-a] => t%',
      '_[t.] => a',
      't%[a] => t',
    ].join('\n'),
  },
  {
    key: 'b3s23',
    name: 'B3/S23',
    text: [
      '_[a]3[_]3 => a',
      'a[a]2[_|a][_]3 => a',
      'a[_|a][_]5 | a[a]4[_|a][_|a] => _',
    ].join('\n'),
  },
]

export function RulesPanel({ sessionId, rulesText, onRulesChange }: Props) {
  const [preset, setPreset] = useState(PRESETS[0].key)

  useEffect(() => {
    // Initialize with default preset only if empty
    if (!rulesText) onRulesChange(PRESETS[0].text)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function applyPreset(key: string) {
    setPreset(key)
    const p = PRESETS.find(p => p.key === key)
    if (p) onRulesChange(p.text)
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', gap: 4, alignItems: 'center', marginBottom: 6, flexShrink: 0 }}>
        <label style={{ fontSize: '11px' }}>Preset:</label>
        <select value={preset} onChange={(e) => applyPreset(e.target.value)} disabled={!sessionId} style={{ flex: 1, fontSize: '11px', padding: '2px 4px' }}>
          {PRESETS.map(p => <option value={p.key} key={p.key}>{p.name}</option>)}
        </select>
      </div>
      <textarea
        value={rulesText}
        onChange={(e) => onRulesChange(e.target.value)}
        style={{ flex: 1, width: '100%', fontFamily: 'monospace', fontSize: '11px', resize: 'none', minHeight: 0, border: '1px solid #ccc', borderRadius: 4, padding: 6 }}
        placeholder="Enter HexiDirect rules, one per line"
        disabled={!sessionId}
      />
    </div>
  )
}
