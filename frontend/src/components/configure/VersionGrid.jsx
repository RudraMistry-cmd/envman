import VersionCard from './VersionCard'

export default function VersionGrid({ versions, selected, onSelect }) {
  return (
    <div className="flex gap-2">
      {versions.map(v => (
        <VersionCard
          key={v.value}
          value={v.value}
          label={v.label}
          badge={v.badge}
          selected={selected === v.value}
          service={v.service}
          onSelect={() => onSelect(v.value)}
        />
      ))}
    </div>
  )
}
