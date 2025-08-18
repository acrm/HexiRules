export type Session = { session_id: string }
export type HistoryItem = { index: number; active_count: number }
export type Cell = [number, number, string, number | null]

async function j<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  const res = await fetch(input, init)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

export async function createSession(): Promise<string> {
  const s = await j<Session>('/session', { method: 'POST' })
  return s.session_id
}

export async function createWorld(session_id: string, name: string, radius: number, rules_text = ''): Promise<void> {
  await j('/world?session_id=' + encodeURIComponent(session_id), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, radius, rules_text }),
  })
}

export async function listHistory(session_id: string): Promise<HistoryItem[]> {
  return j<HistoryItem[]>('/history?session_id=' + encodeURIComponent(session_id))
}

export async function getLogs(session_id: string, index: number): Promise<string[]> {
  return j<string[]>('/history/logs?session_id=' + encodeURIComponent(session_id) + '&index=' + index)
}

export async function step(session_id: string, rules_text?: string): Promise<string[]> {
  return j<string[]>('/step?session_id=' + encodeURIComponent(session_id), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rules_text }),
  })
}

export async function go(session_id: string, index: number): Promise<void> {
  await j('/history/go?session_id=' + encodeURIComponent(session_id) + '&index=' + index, { method: 'POST' })
}

export async function prev(session_id: string): Promise<void> {
  await j('/history/prev?session_id=' + encodeURIComponent(session_id), { method: 'POST' })
}

export async function next_(session_id: string): Promise<void> {
  await j('/history/next?session_id=' + encodeURIComponent(session_id), { method: 'POST' })
}

export async function getCells(session_id: string, index: number): Promise<Cell[]> {
  return j<Cell[]>('/history/cells?session_id=' + encodeURIComponent(session_id) + '&index=' + index)
}
