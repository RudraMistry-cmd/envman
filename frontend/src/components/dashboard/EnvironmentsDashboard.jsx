import { useState, useEffect } from 'react'
import Button from '../shared/Button'
import { TrashIcon, PlusIcon } from '../shared/icons'

const API = 'http://localhost:8000'

export default function EnvironmentsDashboard({ onNew }) {
  const [environments, setEnvironments] = useState([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(null)

  useEffect(() => {
    fetchEnvironments()
  }, [])

  const fetchEnvironments = async () => {
    try {
      const res = await fetch(`${API}/environments`)
      const data = await res.json()
      setEnvironments(data)
    } catch (e) {
      console.error('Failed to fetch environments:', e)
    } finally {
      setLoading(false)
    }
  }

  const deleteEnvironment = async (envId) => {
    setDeleting(envId)
    try {
      await fetch(`${API}/environments/${envId}`, { method: 'DELETE' })
      setEnvironments(prev => prev.filter(e => e.id !== envId))
    } catch (e) {
      console.error('Failed to delete environment:', e)
    } finally {
      setDeleting(null)
    }
  }

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
                  <span className="text-xs text-zinc-600">
                    {env.network_name}
                  </span>
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
                      <span className={`w-1.5 h-1.5 rounded-full ${
                        c.status === 'running' ? 'bg-green-400' : 'bg-zinc-500'
                      }`} />
                      {c.name}
                    </span>
                  ))}
                  {env.containers.length === 0 && (
                    <span className="text-xs text-zinc-600">No containers</span>
                  )}
                </div>
              </div>
              <button
                onClick={() => deleteEnvironment(env.id)}
                disabled={deleting === env.id}
                className="ml-4 p-2 rounded-lg text-zinc-500 hover:text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-50"
                title="Delete environment"
              >
                <TrashIcon className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
