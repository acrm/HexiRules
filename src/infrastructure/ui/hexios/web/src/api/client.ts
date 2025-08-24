export type Session = { session_id: string }
export type HistoryItem = { index: number; active_count: number }
export type Cell = [number, number, string, number | null]

async function j<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  const res = await fetch(input, init)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

export async function createSession(): Promise<string> {
  const s = await j<Session>('/api/session', { method: 'POST' })
  return s.session_id
}

export async function createWorld(session_id: string, name: string, radius: number, rules_text = ''): Promise<void> {
  await j('/api/world?session_id=' + encodeURIComponent(session_id), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, radius, rules_text }),
  })
}

export async function listHistory(session_id: string): Promise<HistoryItem[]> {
  return j<HistoryItem[]>('/api/history?session_id=' + encodeURIComponent(session_id))
}

export async function getLogs(session_id: string, index: number): Promise<string[]> {
  return j<string[]>('/api/history/logs?session_id=' + encodeURIComponent(session_id) + '&index=' + index)
}

export async function step(session_id: string, rules_text?: string): Promise<string[]> {
  return j<string[]>('/api/step?session_id=' + encodeURIComponent(session_id), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rules_text }),
  })
}

export async function go(session_id: string, index: number): Promise<void> {
  await j('/api/history/go?session_id=' + encodeURIComponent(session_id) + '&index=' + index, { method: 'POST' })
}

export async function prev(session_id: string): Promise<void> {
  await j('/api/history/prev?session_id=' + encodeURIComponent(session_id), { method: 'POST' })
}

export async function next_(session_id: string): Promise<void> {
  await j('/api/history/next?session_id=' + encodeURIComponent(session_id), { method: 'POST' })
}

export async function getCells(session_id: string, index: number): Promise<Cell[]> {
  return j<Cell[]>('/api/history/cells?session_id=' + encodeURIComponent(session_id) + '&index=' + index)
}

export async function listWorlds(session_id: string): Promise<{name:string; radius:number; active_count:number}[]> {
  return j('/api/worlds?session_id=' + encodeURIComponent(session_id))
}

export async function selectWorld(session_id: string, name: string): Promise<void> {
  await j('/api/world/select?session_id=' + encodeURIComponent(session_id) + '&name=' + encodeURIComponent(name), { method: 'POST' })
}

export async function renameWorld(session_id: string, old_name: string, new_name: string): Promise<void> {
  await j('/api/world/rename?session_id=' + encodeURIComponent(session_id), {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ old_name, new_name })
  })
}

export async function deleteWorld(session_id: string, name: string): Promise<void> {
  await j('/api/world/delete?session_id=' + encodeURIComponent(session_id) + '&name=' + encodeURIComponent(name), { method: 'POST' })
}

export async function cellsClear(session_id: string): Promise<void> {
  await j('/api/cells/clear?session_id=' + encodeURIComponent(session_id), { method: 'POST' })
}

export async function cellsRandom(session_id: string, states: string[], p = 0.3): Promise<void> {
  await j('/api/cells/random?session_id=' + encodeURIComponent(session_id), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ states, p }) })
}

export async function cellsSet(session_id: string, q: number, r: number, state: string, direction: number | null): Promise<void> {
  await j('/api/cells/set?session_id=' + encodeURIComponent(session_id), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ q, r, state, direction }) })
}

export async function cellsCurrent(session_id: string): Promise<Cell[]> {
  return j<Cell[]>('/api/cells/current?session_id=' + encodeURIComponent(session_id))
}
