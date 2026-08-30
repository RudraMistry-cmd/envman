import { ClockIcon, CheckCircleIcon } from '../shared/icons'

export default function StatsRow({ duration, stepCount, completedCount }) {
  return (
    <div className="flex items-center justify-center gap-6 mb-6">
      {duration && (
        <div className="flex items-center gap-1.5 text-zinc-400">
          <ClockIcon className="w-3.5 h-3.5" />
          <span className="text-sm font-mono">{(duration / 1000).toFixed(1)}s</span>
        </div>
      )}
      {duration && stepCount > 0 && <div className="w-px h-4 bg-white/[0.08]" />}
      {stepCount > 0 && (
        <div className="flex items-center gap-1.5 text-zinc-400">
          <CheckCircleIcon className="w-3.5 h-3.5" />
          <span className="text-sm font-mono">{completedCount}/{stepCount} steps</span>
        </div>
      )}
    </div>
  )
}
