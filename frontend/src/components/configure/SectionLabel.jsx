export default function SectionLabel({ children }) {
  return (
    <div className="flex items-center gap-3 mb-3">
      <span className="text-[11px] font-medium tracking-widest uppercase text-zinc-500">
        {children}
      </span>
      <div className="flex-1 h-px bg-white/[0.06]" />
    </div>
  )
}
