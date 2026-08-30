const colors = {
  ready: 'bg-green-900/50 text-green-300 border-green-800',
  failed: 'bg-red-900/50 text-red-300 border-red-800',
  not_found: 'bg-yellow-900/50 text-yellow-300 border-yellow-800',
  not_running: 'bg-yellow-900/50 text-yellow-300 border-yellow-800',
  not_ready: 'bg-yellow-900/50 text-yellow-300 border-yellow-800',
  not_tracked: 'bg-zinc-800 text-zinc-400 border-zinc-700',
}

export default function StatusBadge({ status }) {
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full border ${colors[status] || colors.not_tracked}`}>
      {status}
    </span>
  )
}
