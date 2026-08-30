import SectionLabel from './SectionLabel'
import VersionGrid from './VersionGrid'
import Button from '../shared/Button'
import { PlayIcon } from '../shared/icons'

const nodeVersions = [
  { value: '18', label: 'Node 18', badge: 'LTS', service: 'node' },
  { value: '20', label: 'Node 20', badge: 'LTS', service: 'node' },
  { value: '22', label: 'Node 22', badge: '', service: 'node' },
]

const postgresVersions = [
  { value: '14', label: 'PostgreSQL 14', service: 'postgres' },
  { value: '15', label: 'PostgreSQL 15', service: 'postgres' },
  { value: '16', label: 'PostgreSQL 16', service: 'postgres' },
  { value: '17', label: 'PostgreSQL 17', service: 'postgres' },
]

export default function ConfigureScreen({ config, setConfig, onStart }) {
  return (
    <div className="animate-screen-enter">
      <h2 className="text-xl font-semibold text-white mb-1">Configure Your Stack</h2>
      <p className="text-sm text-zinc-500 mb-6">Choose the services and versions you need.</p>

      <div className="space-y-5">
        <div>
          <SectionLabel>Runtime</SectionLabel>
          <VersionGrid
            versions={nodeVersions}
            selected={config.node}
            onSelect={(v) => setConfig({ ...config, node: v })}
          />
        </div>

        <div>
          <SectionLabel>Database</SectionLabel>
          <VersionGrid
            versions={postgresVersions}
            selected={config.postgres}
            onSelect={(v) => setConfig({ ...config, postgres: v })}
          />
        </div>

        <Button onClick={onStart}>
          <PlayIcon className="w-4 h-4" />
          Start Setup
        </Button>
      </div>
    </div>
  )
}
