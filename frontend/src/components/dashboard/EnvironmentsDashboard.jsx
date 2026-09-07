import { useState, useEffect, useCallback } from 'react'
import Button from '../shared/Button'
import { TrashIcon, PlusIcon, RefreshIcon } from '../shared/icons'
import LogPanel from '../shared/LogPanel'
import { API } from '../../apiConfig'

function formatNetworkName(name) {
  if (!name) return ''
  if (name.startsWith('envman_net_')) {
    const suffix = name.slice('envman_net_'.length)
    if (suffix.length > 8) {
      return `envman_net_${suffix.slice(0, 8)}`
    }
  }
  return name
}

function getEnvironmentStatus(env) {
  if (env.status) return env.status
  if (!env.containers || env.containers.length === 0) return 'not running'
  if (env.containers.every(c => c.status === 'stopped')) return 'stopped'
  if (env.containers.every(c => c.status === 'running')) return 'running'
  return 'partial'
}

export default function EnvironmentsDashboard({ onNew }) {
  const [environments, setEnvironments] = useState([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(null)
  const [logsVisible, setLogsVisible] = useState(null) // {containerName, logs, available, detail}

  useEffect(() => {
    fetchEnvironments()
  }, [])

  const fetchEnvironments = useCallback(async () => {
    try {
      const res = await fetch(`${API}/environments`)
      const data = await res.json()
      setEnvironments(data)
    } catch (e) {
      console.error('Failed to fetch environments:', e)
    } finally {
      setLoading(false)
    }
  }, [])

  const viewContainerLogs = useCallback(async (envId, containerName) => {
    try {
      const res = await fetch(`${API}/environments/${envId}/containers/${containerName}/logs`)
      const data = await res.json()
      setLogsVisible({ envId, containerName, logs: data.logs || '', available: data.available, detail: data.detail })
    } catch (e) {
      console.error('Failed to fetch container logs:', e)
      setLogsVisible({
        envId,
        containerName,
        logs: '',
        available: false,
        detail: 'log fetch failed',
      })
    }
  }, [])

  const deleteEnvironment = useCallback(async (envId) => {
    setDeleting(envId)
    try {
      await fetch(`${API}/environments/${envId}`, { method: 'DELETE' })
      setEnvironments(prev => prev.filter(e => e.id !== envId))
    } catch (e) {
      console.error('Failed to delete environment:', e)
    } finally {
      setDeleting(null)
    }
  }, [])

  const stopEnvironment = useCallback(async (envId) => {
    try {
      await fetch(`${API}/environments/${envId}/stop`, { method: 'POST' })
      await fetchEnvironments()
    } catch (e) {
      console.error('Failed to stop environment:', e)
    }
  }, [fetchEnvironments])

  const startEnvironment = useCallback(async (envId) => {
    try {
      await fetch(`${API}/environments/${envId}/start`, { method: 'POST' })
      await fetchEnvironments()
    } catch (e) {
      console.error('Failed to start environment:', e)
    }
  }, [fetchEnvironments])

  const exportEnvironment = useCallback(async (envId) => {
    try {
      const res = await fetch(API + '/environments/' + envId + '/export', { method: 'POST' })
      const data = await res.json()
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'envman-' + envId.slice(0, 8) + '.json'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (e) {
      console.error('Failed to export environment:', e)
    }
  }, [])

  if (loading) {
    return (
      <div className="animate-screen-enter">
        <h2 className="text-xl font-semibold text-white mb-1">Environments</h2>
        <p className="text-sm text-zinc-500 mb-6">Loading...</p>
      </div>
    )
  }

  return (
    <div className="animate-screen-enter">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-white mb-1">Environments</h2>
          <p className="text-sm text-zinc-500">Your active Docker environments.</p>
        </div>
        <Button onClick={onNew}>
          <PlusIcon className="w-4 h-4" />
          New
        </Button>
      </div>

      {environments.length === 0 ? (
        <div className="text-center py-12 text-zinc-500">
          <p className="text-sm mb-4">No environments yet.</p>
          <Button onClick={onNew}>
            <PlusIcon className="w-4 h-4" />
            Create your first environment
          </Button>
        </div>
      ) : (
        <div className="space-y-3">
          {environments.map(env => (
            <div
              key={env.id}
              className="flex items-center justify-between p-4 rounded-card bg-white/[0.02] border border-white/[0.06]"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium text-white truncate">
                    {env.id.slice(0, 8)}
                  </span>
                  <span className="text-xs text-zinc-600 font-mono" title={env.network_name}>
                    {formatNetworkName(env.network_name)}
                  </span>
                  {(() => {
                    const status = getEnvironmentStatus(env)
                    const badgeClass =
                      status === 'running'
                        ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                        : status === 'stopped'
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        : status === 'partial'
                        ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                        : 'bg-zinc-500/10 text-zinc-400 border border-zinc-500/20'
                    return (
                      <span className={`text-xs px-2 py-0.5 rounded-full ${badgeClass}`}>
                        {status}
                      </span>
                    )
                  })()}
                </div>
                <div className="flex flex-wrap gap-1">
                  {env.containers.map(c => (
                    <span
                      key={c.id}
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${
                        c.status === 'running'
                          ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                          : 'bg-zinc-500/10 text-zinc-500 border border-zinc-500/20'
                      }`}
                    >
                      <span className={`w-1.5 h-1.5 rounded-full ${c.status === 'running' ? 'bg-green-400' : 'bg-zinc-500'}`} />
                      <span className="flex-1 min-w-0 truncate">{c.name}</span>

                      {/* Connection string display with copy button */}
                      {c.connection_string && (
                        <div className="ml-2">
                          <span className="text-xs text-zinc-400 font-mono truncate w-24 pr-2">
                            {c.connection_string}
                          </span>
                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(c.connection_string).then(() => {
                                // Copy action
                              })
                            }}
                            className="text-zinc-600 text-xs hover:text-zinc-300 transition-colors p-1 rounded"
                            title="Copy connection string"
                          >
                            Copy
                          </button>
                        </div>
                      )}

                      {/* View logs button */}
                      <button
                        onClick={() => viewContainerLogs(env.id, c.name)}
                        className="text-zinc-600 text-xs hover:text-zinc-300 transition-colors p-1 rounded"
                        title="View logs"
                      >
                        Logs
                      </button>

                      {/* Fallback when neither host_port nor connection_string */}
                      {!c.host_port && !c.connection_string && (
                        <span className="text-xs text-zinc-500 ml-2">Docker network only</span>
                      )}
                    </span>
                  ))}
                  {env.containers.length === 0 && (
                    <span className="text-xs text-zinc-600">No containers</span>
                  )}
                </div>
              </div>
              <div className="ml-4 flex items-center gap-1">
              <button
                onClick={() => stopEnvironment(env.id)}
                disabled={env.containers.length === 0}
                className="p-2 rounded-lg text-zinc-500 hover:text-amber-400 hover:bg-amber-500/10 transition-colors disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent disabled:hover:text-zinc-500"
                title={env.containers.length === 0 ? "No containers to stop" : "Stop environment"}
              >
                Stop
              </button>
              <button
                onClick={() => startEnvironment(env.id)}
                disabled={env.containers.length === 0}
                className="p-2 rounded-lg text-zinc-500 hover:text-green-400 hover:bg-green-500/10 transition-colors disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent disabled:hover:text-zinc-500"
                title={env.containers.length === 0 ? "No containers to start" : "Start environment"}
              >
                Start
              </button>
              <button
                onClick={() => exportEnvironment(env.id)}
                className="p-2 rounded-lg text-zinc-500 hover:text-blue-400 hover:bg-blue-500/10 transition-colors"
                title="Export environment config"
              >
                Export
              </button>
              <button
                onClick={() => deleteEnvironment(env.id)}
                disabled={deleting === env.id}
                className="p-2 rounded-lg text-zinc-500 hover:text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-50"
                title="Delete environment"
              >
                <TrashIcon className="w-4 h-4" />
              </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Logs modal/panel */}
      {logsVisible && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white/[0.03] rounded-xl border border-white/[0.1] p-6 max-w-2xl w-full max-h-[80vh] overflow-hidden">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-white">
                Logs for {logsVisible.containerName}
              </h3>
              <button
                onClick={() => setLogsVisible(null)}
                className="text-zinc-400 hover:text-white transition-colors"
                title="Close"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="mt-4">
              {logsVisible.available === false ? (
                <div className="p-4 text-zinc-400 text-center text-sm">
                  <p>{logsVisible.detail || 'no logs available'}</p>
                </div>
              ) : (
                <div>
<Button
                  variant="secondary"
                  size="sm"
                  onClick={() => viewContainerLogs(logsVisible.envId, logsVisible.containerName)}
                  className="mb-3 flex items-center gap-2"
                >
                  <RefreshIcon className="w-3.5 h-3.5" />
                  Refresh
                </Button>

                  <div className="h-64 overflow-y-auto whitespace-pre-wrap text-zinc-200 text-xs font-mono">
                    {logsVisible.logs || '(empty)'}
                  </div>
                </div>
              )}

              {logsVisible.available === false && logsVisible.detail !== 'log fetch failed' && (
                <div className="mt-4 p-3 text-xs text-green-400">
                  <p>No logs available for this container.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
