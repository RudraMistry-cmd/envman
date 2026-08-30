import StepIcon from '../shared/StepIcon'

export default function StepItem({ step, index, isLast }) {
  return (
    <div className="animate-step-enter" style={{ animationDelay: `${index * 50}ms` }}>
      <div className={`
        flex items-start gap-3 px-4 py-3 rounded-lg transition-all duration-300
        ${step.status === 'running'
          ? 'bg-blue-500/[0.08] border border-blue-500/20'
          : step.status === 'failed'
            ? 'bg-red-500/[0.08] border border-red-500/20'
            : 'bg-transparent border border-transparent'
        }
      `}>
        <div className="mt-0.5">
          <StepIcon status={step.status} />
        </div>

        <div className="flex-1 min-w-0">
          <p className={`text-sm font-medium truncate ${
            step.status === 'done' ? 'text-zinc-400' :
            step.status === 'failed' ? 'text-red-400' :
            step.status === 'running' ? 'text-white' :
            'text-zinc-500'
          }`}>
            {step.id}
          </p>
          <p className={`text-xs mt-0.5 truncate ${
            step.status === 'running' ? 'text-zinc-400' : 'text-zinc-600'
          }`}>
            {step.message}
          </p>
        </div>

        {step.status === 'done' && (
          <span className="text-xs text-zinc-600 font-mono shrink-0 mt-0.5">done</span>
        )}
        {step.status === 'running' && (
          <div className="flex gap-1 shrink-0 mt-2">
            <span className="w-1 h-1 rounded-full bg-blue-400 animate-pulse" />
            <span className="w-1 h-1 rounded-full bg-blue-400 animate-pulse [animation-delay:150ms]" />
            <span className="w-1 h-1 rounded-full bg-blue-400 animate-pulse [animation-delay:300ms]" />
          </div>
        )}
      </div>

      {!isLast && (
        <div className="ml-[19px] w-px h-2 bg-white/[0.06]" />
      )}
    </div>
  )
}
