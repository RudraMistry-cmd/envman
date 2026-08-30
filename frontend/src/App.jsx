import { useState, useEffect, useRef, useCallback } from 'react'

const API = 'http://localhost:8000'
const WS_URL = 'ws://localhost:8000/ws'

/*
  App.jsx - The Main Frontend
  ===========================

  THREE SCREENS:
    1. Configure  → User picks Node + Postgres versions
    2. Progress   → Shows live setup progress (WebSocket events)
    3. Results    → Shows verification results (ready / failed)

  HOW IT WORKS:
    - User fills in the form, clicks "Start Setup"
    - Frontend POSTs to /setup → backend starts working
    - Frontend opens WebSocket → receives live events
    - Each event updates the UI (step completed, step failed, etc.)
    - Final "done" event shows the results screen
*/

export default function App() {
  const [phase, setPhase] = useState('configure')
  const [config, setConfig] = useState({ node: '20', postgres: '16' })
  const [steps, setSteps] = useState([])
  const [currentStep, setCurrentStep] = useState(null)
  const [verification, setVerification] = useState(null)
  const [error, setError] = useState(null)
  const [duration, setDuration] = useState(null)
  const wsRef = useRef(null)

  const reset = useCallback(() => {
    setPhase('configure')
    setSteps([])
    setCurrentStep(null)
    setVerification(null)
    setError(null)
    setDuration(null)
  }, [])

  // Handle incoming WebSocket messages
  const handleWsMessage = useCallback((event) => {
    const msg = JSON.parse(event.data)

    switch (msg.type) {
      case 'setup_started':
        setSteps([])
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
        // Close WebSocket — terminal event, no more messages expected
        if (wsRef.current) {
          wsRef.current.close()
          wsRef.current = null
        }
        break

      case 'verify_started':
        setCurrentStep(null)
        break

      case 'done':
        setVerification(msg.data.verification)
        setDuration(msg.data.duration_ms)
        setPhase('results')
        // Close WebSocket — setup complete
        if (wsRef.current) {
          wsRef.current.close()
          wsRef.current = null
        }
        break

      case 'setup_failed':
        setError(msg.data.error)
        setPhase('results')
        // Close WebSocket — terminal event
        if (wsRef.current) {
          wsRef.current.close()
          wsRef.current = null
        }
        break
    }
  }, [])

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [])

  const startSetup = async () => {
    setError(null)
    setVerification(null)
    setDuration(null)
    setSteps([])
    setPhase('progress') // Transition immediately to prevent double-click

    try {
      // STEP 1: Connect WebSocket FIRST (before starting backend work)
      const ws = new WebSocket(WS_URL)
      wsRef.current = ws

      await new Promise((resolve, reject) => {
        ws.onopen = resolve
        ws.onerror = () => reject(new Error('WebSocket connection failed. Is the backend running?'))
        // Timeout after 5 seconds
        setTimeout(() => reject(new Error('WebSocket connection timed out')), 5000)
      })

      // WebSocket is now connected — safe to start backend
      ws.onmessage = handleWsMessage

      // STEP 2: Now POST to start setup (events will arrive on the open WebSocket)
      const res = await fetch(`${API}/setup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Setup failed')
      }
      // Progress screen is already showing — WebSocket will deliver events
    } catch (e) {
      setError(e.message)
      setPhase('results')
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white">EnvMan</h1>
          <p className="text-gray-400 mt-1">Deterministic Environment Engine</p>
        </div>

        {/* Card */}
        <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6 shadow-xl">
          {phase === 'configure' && (
            <ConfigureScreen
              config={config}
              setConfig={setConfig}
              onStart={startSetup}
            />
          )}
          {phase === 'progress' && (
            <ProgressScreen steps={steps} currentStep={currentStep} />
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
        </div>
      </div>
    </div>
  )
}


/* ============================================
   SCREEN 1: Configure
   ============================================
   User picks which versions they want.
   Simple form with two dropdowns and a button.
*/

function ConfigureScreen({ config, setConfig, onStart }) {
  return (
    <div>
      <h2 className="text-xl font-semibold text-white mb-1">Configure Your Stack</h2>
      <p className="text-gray-400 text-sm mb-6">Choose the services and versions you need.</p>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Node.js</label>
          <select
            value={config.node}
            onChange={e => setConfig({ ...config, node: e.target.value })}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="18">Node 18 (LTS)</option>
            <option value="20">Node 20 (LTS)</option>
            <option value="22">Node 22</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">PostgreSQL</label>
          <select
            value={config.postgres}
            onChange={e => setConfig({ ...config, postgres: e.target.value })}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="14">PostgreSQL 14</option>
            <option value="15">PostgreSQL 15</option>
            <option value="16">PostgreSQL 16</option>
            <option value="17">PostgreSQL 17</option>
          </select>
        </div>

        <button
          onClick={onStart}
          className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-2.5 rounded-lg transition-colors mt-2"
        >
          Start Setup
        </button>
      </div>
    </div>
  )
}


/* ============================================
   SCREEN 2: Progress
   ============================================
   Shows a list of steps and their status.
   Updates in real-time via WebSocket.
*/

function ProgressScreen({ steps, currentStep }) {
  return (
    <div>
      <h2 className="text-xl font-semibold text-white mb-1">Setting Up...</h2>
      <p className="text-gray-400 text-sm mb-6">Building your environment step by step.</p>

      <div className="space-y-3">
        {steps.map(step => (
          <div
            key={step.id}
            className="flex items-center gap-3 bg-gray-800 rounded-lg px-4 py-3"
          >
            <StepIcon status={step.status} />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{step.id}</p>
              <p className="text-xs text-gray-400 truncate">{step.message}</p>
            </div>
          </div>
        ))}

        {steps.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            <Spinner />
            <p className="mt-2 text-sm">Waiting for first step...</p>
          </div>
        )}
      </div>

      {currentStep && (
        <div className="mt-4 text-center">
          <Spinner />
          <p className="text-xs text-gray-400 mt-1">Running: {currentStep}</p>
        </div>
      )}
    </div>
  )
}


/* ============================================
   SCREEN 3: Results
   ============================================
   Shows verification results or error.
   Green check = ready. Red X = failed.
*/

function ResultsScreen({ steps, verification, error, duration, onReset }) {
  const hasError = error && !verification
  const allReady = verification?.every(v => v.status === 'ready')

  return (
    <div>
      <h2 className="text-xl font-semibold text-white mb-1">
        {hasError ? 'Setup Failed' : allReady ? 'Environment Ready' : 'Setup Complete'}
      </h2>
      <p className="text-gray-400 text-sm mb-6">
        {hasError ? 'Something went wrong during setup.' : 'Here are your verification results.'}
      </p>

      {/* Error banner */}
      {hasError && (
        <div className="bg-red-900/30 border border-red-800 rounded-lg px-4 py-3 mb-4">
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      {/* Step summary */}
      <div className="space-y-2 mb-4">
        {steps.map(step => (
          <div key={step.id} className="flex items-center gap-2 text-sm">
            <StepIcon status={step.status} small />
            <span className={step.status === 'failed' ? 'text-red-400' : 'text-gray-300'}>
              {step.id}
            </span>
          </div>
        ))}
      </div>

      {/* Verification results */}
      {verification && (
        <div className="space-y-3 mb-4">
          <h3 className="text-sm font-medium text-gray-300">Verification</h3>
          {verification.map(v => (
            <div key={v.service} className="bg-gray-800 rounded-lg px-4 py-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-white capitalize">{v.service}</span>
                <StatusBadge status={v.status} />
              </div>
              {v.checks?.map((check, i) => (
                <div key={i} className="flex items-center gap-2 text-xs text-gray-400 ml-1">
                  <span>{check.passed ? '✓' : '✗'}</span>
                  <span>{check.name}</span>
                  <span className="text-gray-500">— {check.detail}</span>
                </div>
              ))}
              {v.version && (
                <p className="text-xs text-gray-500 mt-1">Version: {v.version}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Duration */}
      {duration && (
        <p className="text-xs text-gray-500 mb-4">
          Completed in {(duration / 1000).toFixed(1)}s
        </p>
      )}

      <button
        onClick={onReset}
        className="w-full bg-gray-800 hover:bg-gray-700 text-white font-medium py-2.5 rounded-lg transition-colors"
      >
        New Environment
      </button>
    </div>
  )
}


/* ============================================
   SHARED COMPONENTS
   ============================================
*/

function StepIcon({ status, small }) {
  const size = small ? 'w-4 h-4' : 'w-5 h-5'

  if (status === 'done') {
    return (
      <svg className={`${size} text-green-400 shrink-0`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
      </svg>
    )
  }
  if (status === 'failed') {
    return (
      <svg className={`${size} text-red-400 shrink-0`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
      </svg>
    )
  }
  if (status === 'running') {
    return <Spinner small={small} />
  }
  return (
    <div className={`${size} rounded-full border-2 border-gray-600 shrink-0`} />
  )
}

function Spinner({ small }) {
  const size = small ? 'w-4 h-4' : 'w-6 h-6'
  return (
    <svg className={`${size} text-blue-400 animate-spin shrink-0`} fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  )
}

function StatusBadge({ status }) {
  const colors = {
    ready: 'bg-green-900/50 text-green-300 border-green-800',
    failed: 'bg-red-900/50 text-red-300 border-red-800',
    not_found: 'bg-yellow-900/50 text-yellow-300 border-yellow-800',
    not_running: 'bg-yellow-900/50 text-yellow-300 border-yellow-800',
    not_ready: 'bg-yellow-900/50 text-yellow-300 border-yellow-800',
    not_tracked: 'bg-gray-800 text-gray-400 border-gray-700',
  }

  return (
    <span className={`text-xs px-2 py-0.5 rounded-full border ${colors[status] || colors.not_tracked}`}>
      {status}
    </span>
  )
}
