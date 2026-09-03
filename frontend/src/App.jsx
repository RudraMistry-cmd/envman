import { useState, useCallback } from 'react'
import Background from './components/layout/Background'
import Header from './components/layout/Header'
import GlassCard from './components/layout/GlassCard'
import EnvironmentsDashboard from './components/dashboard/EnvironmentsDashboard'
import ConfigureScreen from './components/configure/ConfigureScreen'
import ProgressScreen from './components/progress/ProgressScreen'
import ResultsScreen from './components/results/ResultsScreen'
import { useWebSocket } from './hooks/useWebSocket'

const API = 'http://localhost:8000'
const WS_URL = 'ws://localhost:8000/ws'

export default function App() {
  const [phase, setPhase] = useState('dashboard')
  const [config, setConfig] = useState({ node: '20', postgres: '16' })
  const [steps, setSteps] = useState([])
  const [currentStep, setCurrentStep] = useState(null)
  const [verification, setVerification] = useState(null)
  const [error, setError] = useState(null)
  const [duration, setDuration] = useState(null)
  const [connected, setConnected] = useState(false)

  const reset = useCallback(() => {
    setPhase('dashboard')
    setSteps([])
    setCurrentStep(null)
    setVerification(null)
    setError(null)
    setDuration(null)
    setConnected(false)
  }, [])

  const handleWsMessage = useCallback((msg) => {
    switch (msg.type) {
      case 'setup_started':
        setSteps([])
        setConnected(true)
        break

      case 'step_started':
        setCurrentStep(msg.data.step)
        setSteps(prev => [...prev, {
          id: msg.data.step,
          status: 'running',
          message: msg.data.message,
        }])
        break

      case 'step_done':
        setSteps(prev => prev.map(s =>
          s.id === msg.data.step
            ? { ...s, status: 'done', message: msg.data.message }
            : s
        ))
        break

      case 'step_failed':
        setSteps(prev => prev.map(s =>
          s.id === msg.data.step
            ? { ...s, status: 'failed', message: msg.data.message }
            : s
        ))
        setError(msg.data.error)
        setPhase('results')
        break

      case 'verify_started':
        setCurrentStep(null)
        break

      case 'done':
        setVerification(msg.data.verification)
        setDuration(msg.data.duration_ms)
        setPhase('results')
        break

      case 'setup_failed':
        setSteps(prev => prev.map(s =>
          s.status === 'running'
            ? { ...s, status: 'failed', message: 'Setup aborted' }
            : s
        ))
        setError(msg.data.error)
        setPhase('results')
        break
    }
  }, [])

  const { connect, close } = useWebSocket(WS_URL, handleWsMessage)

  const startSetup = async () => {
    setError(null)
    setVerification(null)
    setDuration(null)
    setSteps([])
    setPhase('progress')

    try {
      await connect()

      const res = await fetch(`${API}/setup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Setup failed')
      }
    } catch (e) {
      setError(e.message)
      setPhase('results')
      close()
    }
  }

  // Dynamic total: node + postgres each add 3-4 steps (network, pull, container, health)
  const totalExpected = Object.values(config).filter(Boolean).length * 4

  return (
    <div className="min-h-screen flex items-center justify-center p-4 sm:p-6">
      <Background />

      <div className="relative z-10 w-full max-w-xl">
        <Header />

        <GlassCard>
          {phase === 'dashboard' && (
            <EnvironmentsDashboard onNew={() => setPhase('configure')} />
          )}
          {phase === 'configure' && (
            <ConfigureScreen config={config} setConfig={setConfig} onStart={startSetup} onBack={() => setPhase('dashboard')} />
          )}
          {phase === 'progress' && (
            <ProgressScreen
              steps={steps}
              currentStep={currentStep}
              connected={connected}
              totalExpected={totalExpected}
            />
          )}
          {phase === 'results' && (
            <ResultsScreen
              steps={steps}
              verification={verification}
              error={error}
              duration={duration}
              onReset={reset}
            />
          )}
        </GlassCard>
      </div>
    </div>
  )
}
