import ProgressBar from './ProgressBar'
import StepList from './StepList'
import ConnectionStatus from './ConnectionStatus'
import Spinner from '../shared/Spinner'

export default function ProgressScreen({ steps, currentStep, connected, totalExpected }) {
  const completed = steps.filter(s => s.status === 'done' || s.status === 'failed').length

  return (
    <div className="animate-screen-enter">
      <h2 className="text-xl font-semibold text-white mb-1">Setting Up...</h2>
      <p className="text-sm text-zinc-500 mb-6">Building your environment step by step.</p>

      <ProgressBar completed={completed} total={totalExpected} />

      <div className="flex items-center justify-between mb-4">
        <span className="text-xs text-zinc-500 font-mono">
          Step {completed} of {totalExpected}
        </span>
        {currentStep && (
          <span className="text-xs text-zinc-500 truncate ml-2">
            Running: {currentStep}
          </span>
        )}
      </div>

      {steps.length > 0 ? (
        <StepList steps={steps} />
      ) : (
        <div className="text-center text-zinc-500 py-8">
          <Spinner />
          <p className="mt-3 text-sm">Waiting for first step...</p>
        </div>
      )}

      <ConnectionStatus connected={connected} />
    </div>
  )
}
