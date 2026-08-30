export default function GlassCard({ children, className = '' }) {
  return (
    <div className={`glass-card p-6 sm:p-8 ${className}`}>
      {children}
    </div>
  )
}
