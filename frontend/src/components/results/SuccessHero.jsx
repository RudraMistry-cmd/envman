import { CheckIcon } from '../shared/icons'

export default function SuccessHero() {
  return (
    <div className="relative flex items-center justify-center mb-6">
      <div className="absolute w-24 h-24 rounded-full bg-green-500/10 animate-pulse-glow" />
      <div className="relative w-16 h-16 rounded-full bg-green-500/20 border border-green-500/30 flex items-center justify-center animate-scale-in">
        <CheckIcon className="w-8 h-8 text-green-400" />
      </div>
    </div>
  )
}
