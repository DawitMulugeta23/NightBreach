import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
} from 'lucide-react'

import StatusBadge from '../common/StatusBadge.jsx'

function ModuleCard({
  module,
  progress = null,
  onOpen,
}) {
  const status =
    progress?.status || 'NOT_STARTED'

  return (
    <article className="nb-card nb-card-hover rounded-2xl p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-blue-500/20 bg-blue-500/10">
          <BookOpen className="h-5 w-5 text-blue-400" />
        </div>

        <StatusBadge
          tone={
            status === 'COMPLETED'
              ? 'green'
              : status === 'IN_PROGRESS'
                ? 'blue'
                : 'gray'
          }
        >
          {status === 'COMPLETED'
            ? 'Completed'
            : status === 'IN_PROGRESS'
              ? 'In Progress'
              : 'Not Started'}
        </StatusBadge>
      </div>

      <h3 className="mt-5 font-bold text-white">
        {module.title}
      </h3>

      <p className="mt-2 text-sm leading-6 text-slate-500">
        {module.description}
      </p>

      <button
        type="button"
        onClick={() => onOpen?.(module)}
        className="nb-button-secondary mt-5 flex w-full items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold"
      >
        Open Module

        {status === 'COMPLETED' ? (
          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
        ) : (
          <ArrowRight className="h-4 w-4" />
        )}
      </button>
    </article>
  )
}

export default ModuleCard
