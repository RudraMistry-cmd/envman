import { useState, useCallback, useEffect } from 'react'

const API = 'http://localhost:8000'

function logsUrl(envId, containerName) {
  return API + '/environments/' + envId + '/containers/' + containerName + '/logs'
}

export default function LogPanel({ envId, containerName, className }) {
  const [state, setState] = useState('loading')
  const [logs, setLogs] = useState('')
  const [detail, setDetail] = useState('')

  const fetchLogs = useCallback(async () => {
    setState('loading')
    try {
      const res = await fetch(logsUrl(envId, containerName))
      const data = await res.json()
      if (!data.available) {
        setState('empty')
        setLogs('')
        setDetail(data.detail || 'No logs available')
        return
      }
      setState('available')
      setLogs(data.logs || '')
      setDetail('')
    } catch (e) {
      setState('empty')
      setLogs('')
      setDetail('Failed to fetch logs')
    }
  }, [envId, containerName])

  useEffect(() => {
    fetchLogs()
  }, [fetchLogs])

  return (
    <div className={className || ''}>
      <div className="flex items-center gap-2 mb-2">
        <button
          onClick={fetchLogs}
          className="text-xs px-2 py-1 rounded bg-white/5 border border-white/10 text-zinc-300 hover:bg-white/10"
          title="Refresh logs"
        >
          Refresh
        </button>
        <span className="text-xs text-zinc-500 font-mono truncate">
          {containerName}
        </span>
      </div>

      {state === 'loading' ? (
        <div className="text-xs text-zinc-500">Loading logs...</div>
      ) : state === 'available' ? (
        <pre className="max-h-80 overflow-auto whitespace-pre-wrap font-mono text-xs text-zinc-100 bg-black/30 rounded p-3">
          {logs}
        </pre>
      ) : (
        <div className="text-center text-zinc-500 text-xs py-4">
          <p className="mb-1">{detail || 'No logs available'}</p>
        </div>
      )}
    </div>
  )
}
