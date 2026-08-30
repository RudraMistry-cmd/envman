export default function ConnectionStatus({ connected }) {
  return (
    <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.02] border border-white/[0.04] mt-4">
      <div className={`w-1.5 h-1.5 rounded-full transition-colors ${
        connected ? 'bg-green-400 animate-pulse' : 'bg-zinc-600'
      }`} />
      <span className="text-xs text-zinc-500">
        {connected ? 'Live — receiving events' : 'Connecting...'}
      </span>
    </div>
  )
}
