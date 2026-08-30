import { CheckIcon, XIcon } from './icons'

export default function StepIcon({ status, size = 'md' }) {
  const s = size === 'sm' ? 'w-4 h-4' : 'w-5 h-5'
  const iconSize = size === 'sm' ? 'w-2.5 h-2.5' : 'w-3 h-3'

  if (status === 'done') {
    return (
      <div className={`${s} rounded-full bg-green-500/20 flex items-center justify-center shrink-0`}>
        <CheckIcon className={`${iconSize} text-green-400`} />
      </div>
    )
  }

  if (status === 'failed') {
    return (
      <div className={`${s} rounded-full bg-red-500/20 flex items-center justify-center shrink-0`}>
        <XIcon className={`${iconSize} text-red-400`} />
      </div>
    )
  }

  if (status === 'running') {
    return (
      <div className={`${s} relative flex items-center justify-center shrink-0`}>
        <svg className={`${s} text-blue-400 animate-spin`} fill="none" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2.5" className="opacity-20" />
          <path d="M4 12a8 8 0 018-8" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
        </svg>
        <div className="absolute w-1.5 h-1.5 rounded-full bg-blue-400" />
      </div>
    )
  }

  return (
    <div className={`${s} rounded-full border-[1.5px] border-zinc-700 shrink-0`} />
  )
}
