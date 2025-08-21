import React, { useEffect, useState } from 'react'
import { createSession, step } from '../api/client'
import { WorldsPanel } from './WorldsPanel'
import { GridPanel } from './GridPanel'
import { RulesPanel } from './RulesPanel'
import { HistoryPanel } from './HistoryPanel'
import { StepLogPanel } from './StepLogPanel'

export function App() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [worldName, setWorldName] = useState<string | null>(null)
  const [rulesText, setRulesText] = useState<string>("")
  const [gridRefreshTrigger, setGridRefreshTrigger] = useState<number>(0)
  const [historyRefreshTrigger, setHistoryRefreshTrigger] = useState<number>(0)
  const [stepLogs, setStepLogs] = useState<string[]>([])
  
  function refreshGrid() { setGridRefreshTrigger(prev => prev + 1) }
  function refreshHistory() { setHistoryRefreshTrigger(prev => prev + 1) }
  function addStepLog(msg: string) { setStepLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${msg}`]) }
  function clearStepLog() { setStepLogs([]) }

  useEffect(() => {
    (async () => {
      try {
        console.log('Creating session…')
        const sid = await createSession()
        setSessionId(sid)
        console.log('Session ready: ' + sid)
      } catch (e: any) {
        console.error('Error creating session: ' + (e?.message || e))
      }
    })()
  }, [])

  return (
    <div style={{ padding: 12, display: 'grid', gridTemplateColumns: 'minmax(320px, 400px) 1fr', gap: 12, height: '100vh', boxSizing: 'border-box', minWidth: 600, minHeight: 400 }}>
      {/* Left: Control Panel (responsive width) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gridTemplateRows: '1fr 1fr', gap: 6, height: '100%', overflow: 'hidden' }}>
        {/* Top left: Worlds */}
        <div style={{ gridColumn: 1, gridRow: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <h3 style={{ margin: '0 0 6px 0', fontSize: '12px', fontWeight: 'bold' }}>Worlds</h3>
          <div style={{ flex: 1, overflow: 'hidden', minHeight: 0 }}>
            <WorldsPanel 
              sessionId={sessionId} 
              onLog={console.log} 
              onWorldChange={(n) => {
                setWorldName(n)
                clearStepLog() // Clear step log when switching worlds
                refreshGrid()
                refreshHistory()
              }} 
            />
          </div>
        </div>
        
        {/* Top right: Rules */}
        <div style={{ gridColumn: 2, gridRow: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <h3 style={{ margin: '0 0 6px 0', fontSize: '12px', fontWeight: 'bold' }}>Rules</h3>
          <div style={{ flex: 1, overflow: 'hidden', minHeight: 0 }}>
            <RulesPanel
              sessionId={sessionId}
              rulesText={rulesText}
              onRulesChange={setRulesText}
            />
          </div>
        </div>
        
        {/* Bottom left: History */}
        <div style={{ gridColumn: 1, gridRow: 2, overflow: 'hidden', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <h3 style={{ margin: '0 0 6px 0', fontSize: '12px', fontWeight: 'bold' }}>History</h3>
          <div style={{ flex: 1, overflow: 'hidden', minHeight: 0 }}>
            <HistoryPanel 
              sessionId={sessionId} 
              refreshTrigger={historyRefreshTrigger}
              onSelectIndex={() => {
                clearStepLog() // Clear step log when selecting history item
                refreshGrid()
              }}
              onProgress={async () => {
                if (!sessionId) return
                try {
                  clearStepLog() // Clear previous step logs
                  const logs = await step(sessionId, rulesText)
                  logs.forEach(addStepLog)
                  refreshGrid()
                  refreshHistory()
                } catch (e: any) {
                  addStepLog('Error stepping: ' + (e?.message || e))
                }
              }} 
            />
          </div>
        </div>
        
        {/* Bottom right: Step Log */}
        <div style={{ gridColumn: 2, gridRow: 2, overflow: 'hidden', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <h3 style={{ margin: '0 0 6px 0', fontSize: '12px', fontWeight: 'bold' }}>Step Log</h3>
          <div style={{ flex: 1, overflow: 'hidden', minHeight: 0 }}>
            <StepLogPanel logs={stepLogs} onClear={clearStepLog} />
          </div>
        </div>
      </div>
      
      {/* Right: Grid fills remaining space */}
      <div style={{ minWidth: 0, height: '100%' }}>
        <GridPanel 
          sessionId={sessionId} 
          worldName={worldName} 
          onLog={addStepLog} 
          rulesText={rulesText} 
          refreshTrigger={gridRefreshTrigger} 
        />
      </div>
    </div>
  )
}
