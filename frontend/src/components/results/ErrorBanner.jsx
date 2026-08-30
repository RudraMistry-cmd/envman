import { AlertTriangleIcon } from '../shared/icons'

export default function ErrorBanner({ error }) {
  return (
    <div className="rounded-card border border-red-500/20 bg-red-500/[0.06] px-4 py-3 mb-4 animate-slide-down">
      <div className="flex items-start gap-3">
        <AlertTriangleIcon className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
        <div>
          <p className="text-sm font-medium text-red-300">Setup Failed</p>
          <p className="text-xs text-red-400/70 mt-0.5">{error}</p>
        </div>
      </div>
    </div>
  )
}
