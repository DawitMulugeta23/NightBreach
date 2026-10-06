import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  Layers3,
} from 'lucide-react'

import ProgressBar from '../common/ProgressBar.jsx'
import StatusBadge from '../common/StatusBadge.jsx'
import nightbreachAssets from '../../config/nightbreachAssets.js'

const pathIcons = {
  linux: nightbreachAssets.icons.linux,
  windows: nightbreachAssets.icons.windows,
  'cyber-security': nightbreachAssets.icons.cyberSecurity,
  networking: nightbreachAssets.icons.networking,
  'offensive-security': nightbreachAssets.icons.offensiveSecurity,
  'defensive-security': nightbreachAssets.icons.defensiveSecurity,
}

const pathTones = {
  linux: 'blue',
  windows: 'blue',
  'cyber-security': 'green',
  networking: 'purple',
  'offensive-security': 'red',
  'defensive-security': 'orange',
}

const toneStyles = {
  blue: {
    border: 'border-blue-500/20',
    background: 'bg-blue-500/10',
    text: 'text-blue-400',
    glow: 'bg-blue-500/10',
  },
  green: {
    border: 'border-emerald-500/20',
    background: 'bg-emerald-500/10',
    text: 'text-emerald-400',
    glow: 'bg-emerald-500/10',
  },
  purple: {
    border: 'border-purple-500/20',
    background: 'bg-purple-500/10',
    text: 'text-purple-400',
    glow: 'bg-purple-500/10',
  },
  red: {
    border: 'border-red-500/20',
    background: 'bg-red-500/10',
    text: 'text-red-400',
    glow: 'bg-red-500/10',
  },
  orange: {
    border: 'border-orange-500/20',
    background: 'bg-orange-500/10',
    text: 'text-orange-400',
    glow: 'bg-orange-500/10',
  },
}

function getIcon(slug) {
  return (
    pathIcons[String(slug || '').toLowerCase()] ||
    nightbreachAssets.icons.cyberSecurity
  )
}

function getTone(slug) {
  return (
    pathTones[String(slug || '').toLowerCase()] ||
    'blue'
  )
}

function LearningPathCard({
  path,
  progress = null,
  onOpen,
}) {
  const tone = toneStyles[getTone(path.slug)] || toneStyles.blue

  const status =
    progress?.status || 'NOT_STARTED'

  const progressValue =
    status === 'COMPLETED'
      ? 100
      : status === 'IN_PROGRESS'
        ? 50
        : 0

  const modulesCount =
    Array.isArray(path.modules)
      ? path.modules.length
      : null

  return (
    <article
      className="nb-card nb-card-hover group relative overflow-hidden rounded-2xl p-5"
    >
      <div
        className={[
          'pointer-events-none absolute -right-14 -top-14 h-36 w-36 rounded-full blur-3xl opacity-40 transition duration-300 group-hover:opacity-70',
          tone.glow,
        ].join(' ')}
      />

      <div className="relative">
        <div className="flex items-start justify-between gap-4">
          <div
            className={[
              'flex h-14 w-14 shrink-0 items-center justify-center rounded-xl border transition duration-200 group-hover:scale-105',
              tone.border,
              tone.background,
            ].join(' ')}
          >
            <img
              src={getIcon(path.slug)}
              alt=""
              className="h-9 w-9 object-contain"
            />
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

        <div className="mt-5">
          <h2 className="text-lg font-bold tracking-tight text-white">
            {path.title}
          </h2>

          <p className="mt-2 min-h-[48px] text-sm leading-6 text-slate-400">
            {path.description}
          </p>
        </div>

        <div className="mt-5 grid grid-cols-2 divide-x divide-slate-800/80 rounded-xl border border-slate-800/70 bg-slate-950/30 py-3">
          <div className="flex items-center gap-2 px-3">
            <Layers3 className="h-4 w-4 text-slate-500" />

            <div>
              <div className="text-[10px] uppercase tracking-wide text-slate-600">
                Modules
              </div>

              <div className="mt-1 text-sm font-semibold text-slate-200">
                {modulesCount ?? '—'}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 px-3">
            <BookOpen className="h-4 w-4 text-slate-500" />

            <div>
              <div className="text-[10px] uppercase tracking-wide text-slate-600">
                Position
              </div>

              <div className="mt-1 text-sm font-semibold text-slate-200">
                {path.position}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-5">
          <div className="mb-2 flex items-center justify-between text-xs">
            <span className="text-slate-500">
              Path progress
            </span>

            <span className="font-semibold text-slate-300">
              {progressValue}%
            </span>
          </div>

          <ProgressBar value={progressValue} />
        </div>

        <button
          type="button"
          onClick={() => onOpen?.(path)}
          className="nb-button-secondary mt-5 flex w-full items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition hover:-translate-y-0.5"
        >
          {status === 'IN_PROGRESS'
            ? 'Continue Path'
            : status === 'COMPLETED'
              ? 'Review Path'
              : 'Start Path'}

          {status === 'COMPLETED' ? (
            <CheckCircle2 className="h-4 w-4" />
          ) : (
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          )}
        </button>
      </div>
    </article>
  )
}

export default LearningPathCard
