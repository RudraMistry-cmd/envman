export default function ProgressBar({ completed, total }) {
  const pct = total > 0 ? (completed / total) * 100 : 0

  return (
    <div className="relative h-1 bg-white/[0.06] rounded-full overflow-hidden mb-6">
      <div
        className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-blue-500 to-violet-400 transition-all duration-700 ease-out"
        style={{ width: `${pct}%` }}
      />
      {pct > 0 && (
        <div
          className="absolute inset-y-0 left-0 rounded-full opacity-40 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"
          style={{ width: `${pct}%`, backgroundSize: '200% 100%' }}
        />
      )}
    </div>
  )
}
