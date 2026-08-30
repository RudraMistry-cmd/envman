import SuccessHero from './SuccessHero'
import ErrorHero from './ErrorHero'
import ErrorBanner from './ErrorBanner'
import StatsRow from './StatsRow'
import ServiceCard from './ServiceCard'
import StepTimeline from './StepTimeline'
import Button from '../shared/Button'
import { RefreshIcon } from '../shared/icons'

export default function ResultsScreen({ steps, verification, error, duration, onReset }) {
  const hasError = error && !verification
  const allReady = verification?.every(v => v.status === 'ready')
  const completedSteps = steps.filter(s => s.status === 'done').length

  return (
    <div className="animate-screen-enter">
      {hasError ? (
        <>
          <ErrorHero />
          <h2 className="text-xl font-semibold text-white mb-1 text-center">Setup Failed</h2>
          <p className="text-sm text-zinc-500 mb-6 text-center">Something went wrong during setup.</p>
        </>
      ) : (
        <>
          <SuccessHero />
          <h2 className="text-xl font-semibold text-white mb-1 text-center">Environment Ready</h2>
          <p className="text-sm text-zinc-500 mb-6 text-center">All services verified and running.</p>
        </>
      )}

      {hasError && <ErrorBanner error={error} />}

      <StatsRow
        duration={duration}
        stepCount={steps.length}
        completedCount={completedSteps}
      />

      {verification && (
        <div className="space-y-3 mb-4">
          <h3 className="text-xs font-medium tracking-widest uppercase text-zinc-500">Verification</h3>
          {verification.map(v => (
            <ServiceCard key={v.service} service={v} />
          ))}
        </div>
      )}

      {steps.length > 0 && (
        <StepTimeline steps={steps} />
      )}

      <Button variant="secondary" onClick={onReset}>
        <RefreshIcon className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
        New Environment
      </Button>
    </div>
  )
}
