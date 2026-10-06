import { CheckCircle2 } from 'lucide-react'

export default function RoomNav({
  roomTitle,
  lessons,
  currentId,
  statusFor,
  onSelect,
}) {
  const completed = lessons.filter(
    (lesson) => statusFor(lesson.id) === 'COMPLETED',
  ).length
  const percent = lessons.length
    ? Math.round((completed / lessons.length) * 100)
    : 0

  return (
    <nav className="nb-card rounded-2xl p-4 lg:sticky lg:top-6">
      <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-600">
        Room
      </div>
      <div className="mt-1 text-sm font-bold text-white">{roomTitle}</div>

      <ol className="mt-4 space-y-1">
        {lessons.map((lesson) => {
          const status = statusFor(lesson.id)
          const active = lesson.id === currentId

          return (
            <li key={lesson.id}>
              <button
                type="button"
                onClick={() => onSelect(lesson.id)}
                className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition ${
                  active
                    ? 'bg-blue-500/10 text-white'
                    : 'text-slate-400 hover:bg-slate-800/40 hover:text-slate-200'
                }`}
              >
                {status === 'COMPLETED' ? (
                  <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
                ) : (
                  <span
                    className={`h-4 w-4 shrink-0 rounded-full border ${
                      active
                        ? 'border-blue-400 bg-blue-400/30'
                        : 'border-slate-700'
                    }`}
                  />
                )}
                <span className="truncate">{lesson.title}</span>
              </button>
            </li>
          )
        })}
      </ol>

      <div className="mt-5 border-t border-slate-800 pt-4">
        <div className="flex justify-between text-xs text-slate-500">
          <span>Progress</span>
          <span>
            {completed}/{lessons.length} · {percent}%
          </span>
        </div>
        <div className="mt-2 h-1.5 rounded-full bg-slate-800">
          <div
            className="h-1.5 rounded-full bg-blue-500 transition-all"
            style={{ width: `${percent}%` }}
          />
        </div>
      </div>
    </nav>
  )
}
