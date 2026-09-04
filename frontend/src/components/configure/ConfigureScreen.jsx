import { useState, useEffect } from 'react'
import CategoryIcon from './CategoryIcon'
import VersionGrid from './VersionGrid'
import Button from '../shared/Button'
import { PlayIcon, ChevronIcon, CheckIcon } from '../shared/icons'

const API = 'http://localhost:8000'

const VERSION_OPTIONS = {
  node: [
    { value: '18', label: 'Node 18', badge: 'LTS', service: 'node' },
    { value: '20', label: 'Node 20', badge: 'LTS', service: 'node' },
    { value: '22', label: 'Node 22', badge: '', service: 'node' },
  ],
  postgres: [
    { value: '14', label: 'PostgreSQL 14', service: 'postgres' },
    { value: '15', label: 'PostgreSQL 15', service: 'postgres' },
    { value: '16', label: 'PostgreSQL 16', service: 'postgres' },
    { value: '17', label: 'PostgreSQL 17', service: 'postgres' },
  ],
  python: [
    { value: '3.11', label: 'Python 3.11', service: 'python' },
    { value: '3.12', label: 'Python 3.12', service: 'python' },
    { value: '3.13', label: 'Python 3.13', badge: 'Latest', service: 'python' },
  ],
  mysql: [
    { value: '8.0', label: 'MySQL 8.0', service: 'mysql' },
    { value: '8.4', label: 'MySQL 8.4', badge: 'Latest', service: 'mysql' },
  ],
  mongo: [
    { value: '6', label: 'MongoDB 6', service: 'mongo' },
    { value: '7', label: 'MongoDB 7', badge: 'Latest', service: 'mongo' },
  ],
  redis: [{ value: '7', label: 'Redis 7', badge: 'Latest', service: 'redis' }],
  elasticsearch: [{ value: '8.14.0', label: 'Elasticsearch 8.14', badge: 'Latest', service: 'elasticsearch' }],
  meilisearch: [{ value: 'v1', label: 'MeiliSearch v1', badge: 'Latest', service: 'meilisearch' }],
  typesense: [{ value: '27.1', label: 'Typesense 27.1', badge: 'Latest', service: 'typesense' }],
  minio: [{ value: 'latest', label: 'MinIO', badge: 'Latest', service: 'minio' }],
  rabbitmq: [{ value: '3', label: 'RabbitMQ 3', badge: 'Latest', service: 'rabbitmq' }],
  kafka: [{ value: '7.5.16', label: 'Kafka 7.5', badge: 'Latest', service: 'kafka' }],
  nats: [{ value: '2', label: 'NATS 2', badge: 'Latest', service: 'nats' }],
  couchdb: [{ value: '3', label: 'CouchDB 3', badge: 'Latest', service: 'couchdb' }],
  sqlite: [{ value: '3', label: 'SQLite 3', badge: 'Embedded', service: 'sqlite' }],
}

const CATEGORY_META = {
  runtime:  { label: 'Runtimes',    tint: 'rgba(59, 130, 246, 0.08)',  iconColor: 'text-blue-400',    selectedBg: 'bg-blue-500/10',    selectedBorder: 'border-blue-500/30' },
  database: { label: 'Databases',   tint: 'rgba(6, 182, 212, 0.08)',   iconColor: 'text-cyan-400',    selectedBg: 'bg-cyan-500/10',    selectedBorder: 'border-cyan-500/30' },
  cache:    { label: 'Caches',      tint: 'rgba(245, 158, 11, 0.08)',  iconColor: 'text-amber-400',   selectedBg: 'bg-amber-500/10',   selectedBorder: 'border-amber-500/30' },
  queue:    { label: 'Queues',      tint: 'rgba(139, 92, 246, 0.08)',  iconColor: 'text-violet-400',  selectedBg: 'bg-violet-500/10',  selectedBorder: 'border-violet-500/30' },
  search:   { label: 'Search',      tint: 'rgba(16, 185, 129, 0.08)',  iconColor: 'text-emerald-400', selectedBg: 'bg-emerald-500/10', selectedBorder: 'border-emerald-500/30' },
  storage:  { label: 'Storage',     tint: 'rgba(148, 163, 184, 0.08)', iconColor: 'text-slate-400',   selectedBg: 'bg-slate-500/10',   selectedBorder: 'border-slate-500/30' },
}

const CATEGORY_ORDER = ['runtime', 'database', 'cache', 'queue', 'search', 'storage']

function getHeadline(svcs) {
  return svcs.map(s => s.name).join(' with ')
}

function getCategorySelectionCount(category, config) {
  const count = Object.keys(config).filter(k => config[k]).length
  return count
}

function countSelectedInCategory(svcs, config) {
  return svcs.filter(s => config[s.id]).length
}

export default function ConfigureScreen({ config, setConfig, onStart, onBack }) {
  const [services, setServices] = useState([])
  const [expandedCategory, setExpandedCategory] = useState(null)

  useEffect(() => {
    fetch(`${API}/registry/services`)
      .then(res => res.json())
      .then(setServices)
      .catch(console.error)
  }, [])

  const grouped = {}
  for (const svc of services) {
    const cat = svc.category || 'other'
    if (!grouped[cat]) grouped[cat] = []
    grouped[cat].push(svc)
  }

  const totalSelected = Object.values(config).filter(Boolean).length

  const toggleService = (serviceId, version) => {
    setConfig(prev => {
      const next = { ...prev }
      if (next[serviceId] === version) {
        delete next[serviceId]
      } else {
        next[serviceId] = version
      }
      return next
    })
  }

  const handleStart = () => {
    // Build proper {services: [...]} payload from registry
    const serviceSpecs = Object.entries(config)
      .filter(([, version]) => version)
      .map(([serviceId, version]) => {
        const registryEntry = services.find(s => s.id === serviceId)
        return {
          name: serviceId,
          image: `${registryEntry.image}:${version}`,
        }
      })
    onStart({ services: serviceSpecs })
  }

  // LEVEL 2: Expanded category detail
  if (expandedCategory && grouped[expandedCategory]) {
    const svcs = grouped[expandedCategory]
    const meta = CATEGORY_META[expandedCategory] || CATEGORY_META.database

    return (
      <div className="animate-screen-enter">
        <div className="flex items-center gap-2 mb-1">
          <button
            onClick={() => setExpandedCategory(null)}
            className="text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            <ChevronIcon className="w-5 h-5 rotate-90" />
          </button>
          <h2 className="text-xl font-semibold text-white">{meta.label}</h2>
        </div>
        <p className="text-sm text-zinc-500 mb-5">
          {svcs.map(s => s.name).join(', ')}
        </p>

        <div className="space-y-2 mb-6">
          {svcs.map(svc => {
            const versions = VERSION_OPTIONS[svc.id] || []
            const selectedVersion = config[svc.id]
            const isSelected = !!selectedVersion
            const hasMultipleVersions = versions.length > 1

            if (!hasMultipleVersions) {
              // Single-version: simple toggle chip
              return (
                <button
                  key={svc.id}
                  onClick={() => toggleService(svc.id, versions[0]?.value || 'latest')}
                  className={`
                    w-full flex items-center gap-3 px-4 py-3 rounded-card
                    border transition-all duration-200 text-left
                    ${isSelected
                      ? `${meta.selectedBg} ${meta.selectedBorder}`
                      : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.04]'
                    }
                  `}
                >
                  <div className={`
                    w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0
                    transition-colors
                    ${isSelected
                      ? 'bg-blue-500 text-white'
                      : 'bg-white/[0.06] text-zinc-500'
                    }
                  `}>
                    {isSelected && <CheckIcon className="w-3.5 h-3.5" />}
                  </div>
                  <span className={`text-sm font-medium ${isSelected ? 'text-white' : 'text-zinc-300'}`}>
                    {svc.name}
                  </span>
                  {versions[0]?.badge && (
                    <span className="text-xs text-zinc-600 ml-auto">{versions[0].badge}</span>
                  )}
                </button>
              )
            }

            // Multi-version: toggle chip + version sub-picker
            return (
              <div key={svc.id}>
                <button
                  onClick={() => {
                    if (isSelected) {
                      toggleService(svc.id, selectedVersion)
                    } else {
                      // Select first version as default
                      toggleService(svc.id, versions[0].value)
                    }
                  }}
                  className={`
                    w-full flex items-center gap-3 px-4 py-3 rounded-card
                    border transition-all duration-200 text-left
                    ${isSelected
                      ? `${meta.selectedBg} ${meta.selectedBorder}`
                      : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.04]'
                    }
                  `}
                >
                  <div className={`
                    w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0
                    transition-colors
                    ${isSelected
                      ? 'bg-blue-500 text-white'
                      : 'bg-white/[0.06] text-zinc-500'
                    }
                  `}>
                    {isSelected && <CheckIcon className="w-3.5 h-3.5" />}
                  </div>
                  <span className={`text-sm font-medium ${isSelected ? 'text-white' : 'text-zinc-300'}`}>
                    {svc.name}
                  </span>
                  {isSelected && (
                    <span className="text-xs text-zinc-500 ml-auto">{selectedVersion}</span>
                  )}
                </button>

                {isSelected && (
                  <div className="ml-9 mt-1.5 mb-1">
                    <VersionGrid
                      versions={versions}
                      selected={selectedVersion}
                      onSelect={(v) => toggleService(svc.id, v)}
                    />
                  </div>
                )}
              </div>
            )
          })}
        </div>

        <Button onClick={handleStart} disabled={totalSelected === 0}>
          <PlayIcon className="w-4 h-4" />
          Start Setup{totalSelected > 0 ? ` (${totalSelected})` : ''}
        </Button>
      </div>
    )
  }

  // LEVEL 1: Category blocks grid
  return (
    <div className="animate-screen-enter">
      <div className="flex items-center gap-2 mb-1">
        {onBack && (
          <button onClick={onBack} className="text-zinc-500 hover:text-zinc-300 transition-colors">
            <ChevronIcon className="w-5 h-5 rotate-90" />
          </button>
        )}
        <h2 className="text-xl font-semibold text-white">Configure Your Stack</h2>
      </div>
      <p className="text-sm text-zinc-500 mb-5">Choose the services and versions you need.</p>

      <div className="grid grid-cols-2 gap-3 mb-5">
        {CATEGORY_ORDER.map(cat => {
          const svcs = grouped[cat] || []
          const meta = CATEGORY_META[cat] || CATEGORY_META.database
          const selectedCount = countSelectedInCategory(svcs, config)

          return (
            <button
              key={cat}
              onClick={() => setExpandedCategory(cat)}
              className={`
                relative flex flex-col items-center text-center
                px-4 py-5 rounded-card border transition-all duration-200
                cursor-pointer group
                ${selectedCount > 0
                  ? `${meta.selectedBg} ${meta.selectedBorder}`
                  : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.04] hover:border-white/[0.12]'
                }
              `}
            >
              <CategoryIcon
                category={cat}
                className={`w-8 h-8 mb-2 transition-colors ${selectedCount > 0 ? meta.iconColor : 'text-zinc-500 group-hover:text-zinc-400'}`}
              />

              <span className={`
                text-xs font-bold uppercase tracking-wider mb-1 transition-colors
                ${selectedCount > 0 ? 'text-white' : 'text-zinc-300'}
              `}>
                {meta.label}
              </span>

              <span className="text-[10px] text-zinc-600 mb-2">
                {svcs.map(s => s.name).join(', ')}
              </span>

              <span className={`
                text-xs px-2 py-0.5 rounded-full transition-colors
                ${selectedCount > 0
                  ? 'bg-blue-500/20 text-blue-300'
                  : 'bg-white/[0.04] text-zinc-500'
                }
              `}>
                {selectedCount > 0 ? `${selectedCount} selected` : `${svcs.length} available`}
              </span>
            </button>
          )
        })}
      </div>

      <Button onClick={handleStart} disabled={totalSelected === 0}>
        <PlayIcon className="w-4 h-4" />
        Start Setup{totalSelected > 0 ? ` (${totalSelected})` : ''}
      </Button>
    </div>
  )
}
