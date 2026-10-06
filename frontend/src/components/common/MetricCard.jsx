function MetricCard({ icon: Icon, label, value, detail, tone = 'blue' }) {
  const tones = {
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    green: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    orange: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
  }

  const isImageIcon = typeof Icon === 'string'

  return (
    <div className="nb-card nb-card-hover rounded-xl p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-[11px] text-slate-500">{label}</div>
          <div className="mt-2 text-2xl font-bold tracking-tight text-white">
            {value}
          </div>
          {detail && (
            <div className="mt-1 text-[10px] text-slate-500">
              {detail}
            </div>
          )}
        </div>

        {Icon && (
          <div
            className={[
              'flex h-9 w-9 items-center justify-center rounded-lg border',
              tones[tone] ?? tones.blue,
            ].join(' ')}
          >
            {isImageIcon ? (
              <img
                src={Icon}
                alt=""
                className="h-5 w-5 object-contain"
              />
            ) : (
              <Icon className="h-4 w-4" />
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default MetricCard
