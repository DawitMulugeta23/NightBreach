function StatusBadge({ children, tone = 'blue' }) {
  const tones = {
    blue: 'border-blue-500/20 bg-blue-500/10 text-blue-300',
    green: 'border-emerald-500/20 bg-emerald-500/10 text-emerald-300',
    purple: 'border-purple-500/20 bg-purple-500/10 text-purple-300',
    orange: 'border-orange-500/20 bg-orange-500/10 text-orange-300',
    red: 'border-red-500/20 bg-red-500/10 text-red-300',
    slate: 'border-slate-700 bg-slate-800/50 text-slate-400',
  }

  return (
    <span
      className={[
        'inline-flex items-center rounded-full border px-2 py-0.5',
        'text-[10px] font-semibold',
        tones[tone] ?? tones.blue,
      ].join(' ')}
    >
      {children}
    </span>
  )
}

export default StatusBadge
