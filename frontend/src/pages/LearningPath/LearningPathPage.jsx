import {
  ArrowLeft,
  BookOpen,
  Layers3,
  Loader2,
  Lock,
  RefreshCw,
} from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import {
  useNavigate,
  useParams,
} from 'react-router-dom'

import SectionHeader from '../../components/common/SectionHeader.jsx'
import ProgressBar from '../../components/common/ProgressBar.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import { getLearningPath } from '../../services/learningService.js'
import { getLearningPathProgress } from '../../services/progressService.js'
import nightbreachAssets from '../../config/nightbreachAssets.js'

function LearningPathPage() {
  const { learningPathId } = useParams()
  const navigate = useNavigate()

  const [path, setPath] = useState(null)
  const [progress, setProgress] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadPath = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const [pathResponse, progressResponse] =
        await Promise.all([
          getLearningPath(learningPathId),
          getLearningPathProgress(learningPathId).catch(
            () => null,
          ),
        ])

      setPath(pathResponse?.data ?? pathResponse)
      setProgress(
        progressResponse?.data ?? progressResponse,
      )
    } catch (requestError) {
      setError(
        requestError?.message ||
          'Unable to load this learning path.',
      )
    } finally {
      setLoading(false)
    }
  }, [learningPathId])

  useEffect(() => {
    let cancelled = false

    async function initialize() {
      setLoading(true)
      setError('')

      try {
        const [pathResponse, progressResponse] =
          await Promise.all([
            getLearningPath(learningPathId),
            getLearningPathProgress(learningPathId).catch(
              () => null,
            ),
          ])

        if (cancelled) {
          return
        }

        setPath(pathResponse?.data ?? pathResponse)
        setProgress(
          progressResponse?.data ?? progressResponse,
        )
      } catch (requestError) {
        if (!cancelled) {
          setError(
            requestError?.message ||
              'Unable to load this learning path.',
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    initialize()

    return () => {
      cancelled = true
    }
  }, [learningPathId])

  const status = progress?.status || 'NOT_STARTED'

  const progressValue =
    status === 'COMPLETED'
      ? 100
      : status === 'IN_PROGRESS'
        ? 50
        : 0

  if (loading) {
    return (
      <PageShell>
        <LoadingState text="Loading learning path..." />
      </PageShell>
    )
  }

  if (error || !path) {
    return (
      <PageShell>
        <ErrorState
          message={error || 'Learning path not found.'}
          onRetry={loadPath}
        />
      </PageShell>
    )
  }

  return (
    <PageShell>
      <button
        type="button"
        onClick={() => navigate('/learning')}
        className="mb-5 inline-flex items-center gap-2 text-sm text-slate-500 transition hover:text-white"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Learning Paths
      </button>

      <div className="mb-6">
        <SectionHeader
          eyebrow="Learning Path"
          title={path.title}
          description={path.description}
        />
      </div>

      <section className="nb-card relative overflow-hidden rounded-2xl p-6">
        <div className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-blue-500/10 blur-3xl" />

        <div className="relative grid gap-6 lg:grid-cols-[1fr_auto]">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-blue-500/20 bg-blue-500/10">
                <img
                  src={nightbreachAssets.icons.learningPaths}
                  alt=""
                  className="h-7 w-7 object-contain"
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

            <div className="mt-6">
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
          </div>

          <div className="flex items-center gap-3 rounded-xl border border-slate-800/70 bg-slate-950/30 px-5 py-4">
            <Layers3 className="h-5 w-5 text-blue-400" />

            <div>
              <div className="text-[10px] uppercase tracking-wider text-slate-600">
                Modules
              </div>

              <div className="mt-1 text-lg font-bold text-white">
                {path.modules?.length ?? 0}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-6">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">
              Modules
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Work through the modules in this learning path.
            </p>
          </div>

          <button
            type="button"
            onClick={loadPath}
            disabled={loading}
            className="rounded-lg border border-slate-800 px-3 py-2 text-slate-400 transition hover:border-slate-700 hover:text-white disabled:opacity-50"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>

        <div className="space-y-3">
          {(path.modules || []).map((module, index) => (
            <button
              key={module.id}
              type="button"
              onClick={() => navigate(`/modules/${module.id}`)}
              className="nb-card nb-card-hover flex w-full items-center gap-4 rounded-xl p-4 text-left"
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-blue-500/20 bg-blue-500/10 text-sm font-bold text-blue-400">
                {index + 1}
              </div>

              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-white">
                    {module.title}
                  </h3>

                  {module.slug && (
                    <span className="hidden text-[10px] text-slate-600 sm:inline">
                      {module.slug}
                    </span>
                  )}
                </div>

                <p className="mt-1 line-clamp-2 text-sm text-slate-500">
                  {module.description}
                </p>
              </div>

              <BookOpen className="h-5 w-5 shrink-0 text-slate-600" />
            </button>
          ))}

          {path.modules?.length === 0 && (
            <div className="rounded-xl border border-slate-800/70 p-8 text-center text-sm text-slate-500">
              No modules are currently available in this path.
            </div>
          )}
        </div>
      </section>
    </PageShell>
  )
}

function PageShell({ children }) {
  return (
    <div className="nb-page nb-grid">
      <div className="mx-auto max-w-[1200px] px-4 py-6 sm:px-6 lg:px-8">
        {children}
      </div>
    </div>
  )
}

function LoadingState({ text }) {
  return (
    <div className="flex min-h-[500px] items-center justify-center">
      <div className="flex items-center gap-3 text-sm text-slate-400">
        <Loader2 className="h-5 w-5 animate-spin text-blue-400" />
        {text}
      </div>
    </div>
  )
}

function ErrorState({ message, onRetry }) {
  return (
    <div className="flex min-h-[500px] items-center justify-center">
      <div className="max-w-md rounded-2xl border border-red-500/20 bg-red-500/5 p-6 text-center">
        <Lock className="mx-auto h-7 w-7 text-red-400" />

        <h2 className="mt-4 font-semibold text-white">
          Unable to load learning path
        </h2>

        <p className="mt-2 text-sm leading-6 text-slate-500">
          {message}
        </p>

        <button
          type="button"
          onClick={onRetry}
          className="nb-button-secondary mt-5 rounded-lg px-4 py-2 text-sm font-semibold"
        >
          Retry
        </button>
      </div>
    </div>
  )
}

export default LearningPathPage
