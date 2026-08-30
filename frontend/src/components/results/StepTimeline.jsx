import { useState } from 'react'
import StepIcon from '../shared/StepIcon'
import { ChevronIcon } from '../shared/icons'

export default function StepTimeline({ steps }) {
  const [expanded, setExpanded] = useState(false)
  const completed = steps.filter(s => s.status === 'done').length

  return (
    <div className="rounded-card border border-white/[0.06] bg-white/[0.02] mb-4">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-4 py-3 text-left"
      >
        <span className="text-xs text-zinc-400 font-mono">
          Show all steps ({completed}/{steps.length})
        </span>
        <ChevronIcon className={`w-4 h-4 text-zinc-600 transition-transform duration-200 ${
          expanded ? 'rotate-180' : ''
        }`} />
      </button>

      {expanded && (
        <div className="px-4 pb-3 border-t border-white/[0.04] pt-3 space-y-2">
          {steps.map(step => (
            <div key={step.id} className="flex items-center gap-2 text-xs">
              <StepIcon status={step.status} size="sm" />
              <span className={
                step.status === 'failed' ? 'text-red-400' : 'text-zinc-400'
              }>
                {step.id}
              </span>
              <span className="text-zinc-600">&mdash;</span>
              <span className="text-zinc-500 truncate">{step.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
