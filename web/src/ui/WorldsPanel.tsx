import React, { useEffect, useState } from 'react'
import { createWorld, deleteWorld, listWorlds, renameWorld, selectWorld } from '../api/client'

type WorldSummary = { name: string; radius: number; active_count: number }

export function WorldsPanel({ sessionId, onLog, onWorldChange }: { sessionId: string | null; onLog: (msg: string) => void; onWorldChange?: (name: string | null) => void }) {
  const [worlds, setWorlds] = useState<WorldSummary[]>([])
  const [currentWorld, setCurrentWorld] = useState<string>('')
  const [busy, setBusy] = useState(false)

  async function refresh() {
    if (!sessionId) return
    try {
      setBusy(true)
      onLog('Fetching worlds…')
      const ws = await listWorlds(sessionId)
      setWorlds(ws)
      if (ws.length && !currentWorld) {
        // Ensure server selection matches UI default
        await selectWorld(sessionId, ws[0].name)
        setCurrentWorld(ws[0].name)
        onWorldChange?.(ws[0].name)
      }
      onLog(`Worlds loaded: ${ws.map(w => w.name).join(', ') || '(none)'}`)
    } catch (e: any) {
      onLog('Error fetching worlds: ' + (e?.message || e))
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => { refresh() }, [sessionId])

  async function switchWorld(name: string) {
    if (!sessionId) return
    try {
      setBusy(true)
      onLog(`Selecting world: ${name}`)
  await selectWorld(sessionId, name)
      setCurrentWorld(name)
      onLog(`Selected world: ${name}`)
  onWorldChange?.(name)
    } catch (e: any) {
      onLog('Error selecting world: ' + (e?.message || e))
    } finally {
      setBusy(false)
    }
  }

  async function newWorld() {
    if (!sessionId) return
    const name = prompt('New world name?', 'World')
    if (!name) return
    if (worlds.some(w => w.name === name)) {
      alert('World with this name already exists.')
      return
    }
    const radius = Number(prompt('Radius?', '20') || '20')
    try {
      setBusy(true)
      onLog(`Creating world "${name}" (R=${radius})…`)
      await createWorld(sessionId, name, radius, '')
  await selectWorld(sessionId, name)
      setCurrentWorld(name)
      await refresh()
      onLog(`World created: ${name}`)
  onWorldChange?.(name)
    } catch (e: any) {
      onLog('Error creating world: ' + (e?.message || e))
    } finally {
      setBusy(false)
    }
  }

  async function renameCur() {
    if (!sessionId || !currentWorld) return
    const newName = prompt('Rename world to?', currentWorld)
    if (!newName || newName === currentWorld) return
    try {
      setBusy(true)
      onLog(`Renaming world ${currentWorld} → ${newName}…`)
  await renameWorld(sessionId, currentWorld, newName)
      setCurrentWorld(newName)
      await refresh()
      onLog(`World renamed to: ${newName}`)
  onWorldChange?.(newName)
    } catch (e: any) {
      onLog('Error renaming world: ' + (e?.message || e))
    } finally {
      setBusy(false)
    }
  }

  async function deleteCur() {
    if (!sessionId || !currentWorld) return
    if (!confirm(`Delete world ${currentWorld}?`)) return
    try {
      setBusy(true)
      onLog(`Deleting world: ${currentWorld}…`)
      await deleteWorld(sessionId, currentWorld)
      const ws = await listWorlds(sessionId)
      setWorlds(ws)
  const fallback = ws[0]?.name || ''
      if (fallback) {
        await selectWorld(sessionId, fallback)
      }
      setCurrentWorld(fallback)
      onLog(`World deleted. Current: ${fallback || '(none)'}`)
  onWorldChange?.(fallback || null)
    } catch (e: any) {
      onLog('Error deleting world: ' + (e?.message || e))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', gap: 4, marginBottom: 6, flexShrink: 0, flexWrap: 'wrap' }}>
        <button onClick={newWorld} disabled={!sessionId || busy} style={{ fontSize: '11px', padding: '3px 6px' }}>New</button>
        <button onClick={renameCur} disabled={!sessionId || busy || !currentWorld} style={{ fontSize: '11px', padding: '3px 6px' }}>Rename</button>
        <button onClick={deleteCur} disabled={!sessionId || busy || !currentWorld} style={{ background: '#fdd', fontSize: '11px', padding: '3px 6px' }}>Delete</button>
      </div>
      <div style={{ border: '1px solid #ccc', borderRadius: 4, flex: 1, overflow: 'auto', minHeight: 0 }}>
        {worlds.map(w => (
          <div key={w.name}
               onClick={() => switchWorld(w.name)}
               style={{ padding: 4, cursor: 'pointer', background: currentWorld === w.name ? '#eef' : 'transparent', display: 'flex', justifyContent: 'space-between', fontSize: '11px', borderBottom: '1px solid #eee' }}>
            <span>{w.name}</span>
            <span style={{ color: '#666' }}>R={w.radius}</span>
          </div>
        ))}
        {(!worlds || worlds.length === 0) && (
          <div style={{ padding: 6, color: '#888', fontSize: '11px' }}>(no worlds)</div>
        )}
      </div>
      <div style={{ marginTop: 6, flexShrink: 0 }}>
        <button onClick={refresh} disabled={!sessionId || busy} style={{ fontSize: '11px', padding: '3px 6px' }}>Refresh</button>
      </div>
    </div>
  )
}
