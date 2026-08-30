export default function Header() {
  return (
    <div className="text-center mb-8 animate-fade-in">
      <div className="inline-flex items-center gap-2 mb-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-glow-sm">
          <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">EnvMan</h1>
      </div>
      <p className="text-sm text-zinc-500">Deterministic Environment Engine</p>
    </div>
  )
}
