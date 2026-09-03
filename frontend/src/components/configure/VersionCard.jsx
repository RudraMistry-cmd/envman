import { CheckIcon, NodeIcon, PostgresIcon, DatabaseIcon, CacheIcon, QueueIcon, SearchIcon, StorageIcon } from '../shared/icons'

const SERVICE_ICONS = {
  node: NodeIcon,
  postgres: PostgresIcon,
  python: DatabaseIcon,
  mysql: DatabaseIcon,
  mongo: DatabaseIcon,
  sqlite: DatabaseIcon,
  couchdb: DatabaseIcon,
  redis: CacheIcon,
  rabbitmq: QueueIcon,
  kafka: QueueIcon,
  nats: QueueIcon,
  elasticsearch: SearchIcon,
  meilisearch: SearchIcon,
  typesense: SearchIcon,
  minio: StorageIcon,
}

export default function VersionCard({ value, label, badge, selected, service, onSelect }) {
  const ServiceIcon = SERVICE_ICONS[service] || DatabaseIcon

  return (
    <button
      onClick={onSelect}
      className={`
        relative flex flex-col items-center justify-center
        px-4 py-4 rounded-card flex-1 min-w-0
        border transition-all duration-200
        cursor-pointer group
        ${selected
          ? 'bg-blue-500/[0.08] border-blue-500/30 shadow-glow-sm'
          : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.06] hover:border-white/[0.12]'
        }
        focus-visible:outline-2 focus-visible:outline-blue-500 focus-visible:outline-offset-2
      `}
    >
      <ServiceIcon className={`w-5 h-5 mb-2 transition-colors ${selected ? 'text-blue-400' : 'text-zinc-500 group-hover:text-zinc-400'}`} />

      <span className={`text-xl font-semibold transition-colors ${selected ? 'text-white' : 'text-zinc-300'}`}>
        {value}
      </span>

      <span className={`text-xs mt-0.5 transition-colors ${selected ? 'text-zinc-400' : 'text-zinc-600'}`}>
        {label}
      </span>

      {badge && (
        <span className={`text-xs mt-0.5 transition-colors ${selected ? 'text-blue-400/70' : 'text-zinc-600'}`}>
          {badge}
        </span>
      )}

      {selected && (
        <div className="absolute top-2 right-2 w-4 h-4 rounded-full bg-blue-500 flex items-center justify-center">
          <CheckIcon className="w-2.5 h-2.5 text-white" />
        </div>
      )}
    </button>
  )
}
