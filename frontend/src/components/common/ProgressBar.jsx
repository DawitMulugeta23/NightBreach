function ProgressBar({ value = 0, tone = 'blue', className = '' }) {
  const tones = {
    blue: 'from-cyan-400 to-blue-500',
    green: 'from-emerald-400 to-green-500',
    purple: 'from-violet-400 to-purple-600',
    orange: 'from-yellow-400 to-orange-500',
    red: 'from-red-400 to-red-600',
  }

  return (
    <div className={`h-1.5 overflow-hidden rounded-full bg-slate-900 ${className}`}>
      <div
        className={`h-full rounded-full bg-gradient-to-r ${tones[tone] ?? tones.blue}`}
        style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
      />
    </div>
  )
}

export default ProgressBar
