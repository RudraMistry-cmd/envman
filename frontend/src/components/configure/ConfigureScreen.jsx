import { useState, useEffect } from 'react'
import SectionLabel from './SectionLabel'
import VersionGrid from './VersionGrid'
import Button from '../shared/Button'
import { PlayIcon, ChevronIcon } from '../shared/icons'

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
  redis: [
    { value: '7', label: 'Redis 7', badge: 'Latest', service: 'redis' },
  ],
  elasticsearch: [
    { value: '8', label: 'Elasticsearch 8', badge: 'Latest', service: 'elasticsearch' },
  ],
  meilisearch: [
    { value: '1', label: 'MeiliSearch 1', badge: 'Latest', service: 'meilisearch' },
  ],
  typesense: [
    { value: '27', label: 'Typesense 27', badge: 'Latest', service: 'typesense' },
  ],
  minio: [
    { value: 'latest', label: 'MinIO', badge: 'Latest', service: 'minio' },
  ],
  rabbitmq: [
    { value: '3', label: 'RabbitMQ 3', badge: 'Latest', service: 'rabbitmq' },
  ],
  kafka: [
    { value: '7', label: 'Kafka 7', badge: 'Latest', service: 'kafka' },
  ],
  nats: [
    { value: '2', label: 'NATS 2', badge: 'Latest', service: 'nats' },
  ],
  couchdb: [
    { value: '3', label: 'CouchDB 3', badge: 'Latest', service: 'couchdb' },
  ],
  sqlite: [
    { value: '3', label: 'SQLite 3', badge: 'Latest', service: 'sqlite' },
  ],
}

const CATEGORY_LABELS = {
  runtime: 'Runtimes',
  database: 'Databases',
  cache: 'Caches',
  queue: 'Message Queues',
  search: 'Search Engines',
  storage: 'Storage',
}

export default function ConfigureScreen({ config, setConfig, onStart, onBack }) {
  const [services, setServices] = useState([])

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
      <p className="text-sm text-zinc-500 mb-6">Choose the services and versions you need.</p>

      <div className="space-y-5">
        {Object.entries(grouped).map(([category, svcs]) => (
          <div key={category}>
            <SectionLabel>{CATEGORY_LABELS[category] || category}</SectionLabel>
            <div className="space-y-3">
              {svcs.map(svc => {
                const versions = VERSION_OPTIONS[svc.id] || []
                if (versions.length === 0) return null
                return (
                  <div key={svc.id}>
                    <VersionGrid
                      versions={versions}
                      selected={config[svc.id]}
                      onSelect={(v) => setConfig({ ...config, [svc.id]: v })}
                    />
                  </div>
                )
              })}
            </div>
          </div>
        ))}

        <Button onClick={onStart}>
          <PlayIcon className="w-4 h-4" />
          Start Setup
        </Button>
      </div>
    </div>
  )
}
