import { useState } from 'react'
import { CheckIcon, XIcon, ChevronIcon } from '../shared/icons'

export default function ServiceCard({ service }) {
  const [expanded, setExpanded] = useState(false)
  const allPassed = service.checks?.every(c => c.passed)

  return (
    <div className={`rounded-card border transition-all duration-200 ${
      allPassed
        ? 'border-green-500/20 bg-green-500/[0.03]'
        : 'border-red-500/20 bg-red-500/[0.03]'
    }`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left"
      >
        <div className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 ${
          allPassed ? 'bg-green-500/20' : 'bg-red-500/20'
        }`}>
          {allPassed
            ? <CheckIcon className="w-3.5 h-3.5 text-green-400" />
            : <XIcon className="w-3.5 h-3.5 text-red-400" />
          }
        </div>

        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-white capitalize">{service.service}</p>
          {service.version && (
            <p className="text-xs text-zinc-500 font-mono">v{service.version}</p>
          )}
        </div>

        <ChevronIcon className={`w-4 h-4 text-zinc-600 transition-transform duration-200 ${
          expanded ? 'rotate-180' : ''
        }`} />
      </button>

      {expanded && service.checks && (
        <div className="px-4 pb-3 border-t border-white/[0.04]">
          <div className="pt-3 space-y-2">
            {service.checks.map((check, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <div className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                  check.passed ? 'bg-green-400' : 'bg-red-400'
                }`} />
                <span className="text-zinc-400">{check.name}</span>
                <span className="text-zinc-600">&mdash;</span>
                <span className="text-zinc-500 truncate">{check.detail}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
