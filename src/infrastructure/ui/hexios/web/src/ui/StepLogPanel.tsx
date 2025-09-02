import React, { useState } from 'react'

type Props = {
  logs: string[]
  onClear: () => void
}

export function StepLogPanel({ logs, onClear }: Props) {
  const [copied, setCopied] = useState<null | 'ok' | 'err'>(null)

  const text = logs.length > 0 ? logs.join('\n') : '(no step logs)'

  async function handleCopy() {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text)
      } else {
        // Fallback for environments where Clipboard API is unavailable
        const ta = document.createElement('textarea')
        ta.value = text
        ta.style.position = 'fixed'
        ta.style.opacity = '0'
        document.body.appendChild(ta)
        ta.focus()
        ta.select()
        document.execCommand('copy')
        document.body.removeChild(ta)
      }
      setCopied('ok')
      setTimeout(() => setCopied(null), 1500)
    } catch (e) {
      setCopied('err')
      setTimeout(() => setCopied(null), 2000)
    }
  }

  function handleDownload() {
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'hexirules-step-log.txt'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6, flexShrink: 0 }}>
        <button onClick={onClear} style={{ fontSize: '11px', padding: '3px 6px' }}>Clear</button>
        <button onClick={handleCopy} style={{ fontSize: '11px', padding: '3px 6px' }}>Copy</button>
        <button onClick={handleDownload} style={{ fontSize: '11px', padding: '3px 6px' }}>Download</button>
        <span style={{ fontSize: '11px', color: copied === 'ok' ? 'green' : copied === 'err' ? 'crimson' : '#666' }}>
          {copied === 'ok' ? 'Copied' : copied === 'err' ? 'Copy failed' : ''}
        </span>
      </div>
      <div style={{ flex: 1, minHeight: 0 }}>
        {/* Use a read-only textarea to make selection and copy trivial in webviews */}
        <textarea
          readOnly
          value={text}
          spellCheck={false}
          style={{
            height: '100%',
            width: '100%',
            boxSizing: 'border-box',
            background: '#111',
            color: '#ddd',
            padding: 6,
            borderRadius: 4,
            margin: 0,
            fontSize: '10px',
            fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
            border: '1px solid #ccc',
            resize: 'none',
          }}
        />
      </div>
    </div>
  )
}
