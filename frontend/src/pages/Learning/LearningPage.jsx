import {
  BookOpen,
  Clock3,
  Globe,
  Loader2,
  RefreshCw,
  Shield,
} from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import SectionHeader from '../../components/common/SectionHeader.jsx'
import LearningPathCard from '../../components/learning/LearningPathCard.jsx'
import { listLearningPaths } from '../../services/learningService.js'
import {
  getLearningPathProgress,
} from '../../services/progressService.js'
import nightbreachAssets from '../../config/nightbreachAssets.js'

function unwrapList(response) {
  if (Array.isArray(response)) {
    return response
  }

  if (Array.isArray(response?.items)) {
    return response.items
  }

  if (Array.isArray(response?.data)) {
    return response.data
  }

  return []
}

function LearningPage() {
  const navigate = useNavigate()

  const [paths, setPaths] = useState([])
  const [progressByPath, setProgressByPath] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadLearningPaths = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const response = await listLearningPaths()
      const learningPaths = unwrapList(response)

      setPaths(learningPaths)

      const progressEntries = await Promise.all(
        learningPaths.map(async (path) => {
          try {
            const progress =
              await getLearningPathProgress(path.id)

            return [path.id, progress]
          } catch {
            return [path.id, null]
          }
        }),
      )

      setProgressByPath(
        Object.fromEntries(progressEntries),
      )
    } catch (requestError) {
      setError(
        requestError?.message ||
          'Unable to load learning paths.',
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    let cancelled = false

    async function initialize() {
      setLoading(true)
      setError('')

      try {
        const response = await listLearningPaths()

        if (cancelled) {
          return
        }

        const learningPaths = unwrapList(response)
        setPaths(learningPaths)

        const progressEntries = await Promise.all(
          learningPaths.map(async (path) => {
            try {
              const progress =
                await getLearningPathProgress(path.id)

              return [path.id, progress]
            } catch {
              return [path.id, null]
            }
          }),
        )

        if (!cancelled) {
          setProgressByPath(
            Object.fromEntries(progressEntries),
          )
        }
      } catch (requestError) {
        if (!cancelled) {
          setError(
            requestError?.message ||
              'Unable to load learning paths.',
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
  }, [])

  function openPath(path) {
    navigate(`/learning-paths/${path.id}`)
  }

  return (
    <div className="nb-page nb-grid">
      <div className="mx-auto max-w-[1500px] px-4 py-6 sm:px-6 lg:px-8">
        <div className="mb-7 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <SectionHeader
            eyebrow="Learning"
            title="Learning Paths"
            description="Build practical cybersecurity skills through structured, hands-on paths."
          />

          <div className="flex items-center gap-3 rounded-xl border border-slate-800/80 bg-slate-950/40 px-4 py-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-blue-500/20 bg-blue-500/10">
              <img
                src={nightbreachAssets.icons.learningPaths}
                alt=""
                className="h-6 w-6 object-contain"
              />
            </div>

            <div>
              <div className="text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-600">
                Available Paths
              </div>

              <div className="mt-0.5 text-sm font-semibold text-slate-200">
                {loading
                  ? 'Loading...'
                  : `${paths.length} learning ${paths.length === 1 ? 'track' : 'tracks'}`}
              </div>
            </div>

            <button
              type="button"
              onClick={loadLearningPaths}
              disabled={loading}
              className="ml-2 rounded-lg border border-slate-800 px-2.5 py-2 text-slate-400 transition hover:border-slate-700 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
              title="Refresh learning paths"
            >
              <RefreshCw
                className={[
                  'h-4 w-4',
                  loading ? 'animate-spin' : '',
                ].join(' ')}
              />
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/5 p-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="font-semibold text-red-300">
                  Could not load learning paths
                </div>

                <p className="mt-1 text-sm text-red-200/70">
                  {error}
                </p>
              </div>

              <button
                type="button"
                onClick={loadLearningPaths}
                className="rounded-lg border border-red-500/20 px-3 py-2 text-xs font-semibold text-red-300 hover:bg-red-500/10"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {loading ? (
          <div className="flex min-h-[360px] items-center justify-center rounded-2xl border border-slate-800/70 bg-slate-950/20">
            <div className="flex items-center gap-3 text-sm text-slate-400">
              <Loader2 className="h-5 w-5 animate-spin text-blue-400" />
              Loading learning paths...
            </div>
          </div>
        ) : paths.length === 0 ? (
          <div className="rounded-2xl border border-slate-800/70 bg-slate-950/20 p-10 text-center">
            <BookOpen className="mx-auto h-8 w-8 text-slate-600" />

            <h2 className="mt-4 text-lg font-semibold text-white">
              No learning paths available
            </h2>

            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
              The backend did not return any published learning paths yet.
            </p>
          </div>
        ) : (
          <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {paths.map((path) => (
              <LearningPathCard
                key={path.id}
                path={path}
                progress={progressByPath[path.id]}
                onOpen={openPath}
              />
            ))}
          </section>
        )}

        <section className="mt-6 grid gap-5 md:grid-cols-3">
          <div className="nb-card group relative overflow-hidden rounded-2xl p-5">
            <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-blue-500/10 blur-2xl" />

            <div className="relative flex h-11 w-11 items-center justify-center rounded-xl border border-blue-500/20 bg-blue-500/10">
              <BookOpen className="h-5 w-5 text-blue-400" />
            </div>

            <h3 className="mt-4 font-semibold text-white">
              Structured Learning
            </h3>

            <p className="mt-2 text-sm leading-6 text-slate-400">
              Progress through modules and lessons in a logical sequence.
            </p>
          </div>

          <div className="nb-card group relative overflow-hidden rounded-2xl p-5">
            <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-cyan-500/10 blur-2xl" />

            <div className="relative flex h-11 w-11 items-center justify-center rounded-xl border border-cyan-500/20 bg-cyan-500/10">
              <img
                src={nightbreachAssets.icons.terminal}
                alt=""
                className="h-6 w-6 object-contain"
              />
            </div>

            <h3 className="mt-4 font-semibold text-white">
              Hands-on Practice
            </h3>

            <p className="mt-2 text-sm leading-6 text-slate-400">
              Apply concepts through practical environments and terminal-based exercises.
            </p>
          </div>

          <div className="nb-card group relative overflow-hidden rounded-2xl p-5">
            <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-emerald-500/10 blur-2xl" />

            <div className="relative flex h-11 w-11 items-center justify-center rounded-xl border border-emerald-500/20 bg-emerald-500/10">
              <Shield className="h-5 w-5 text-emerald-400" />
            </div>

            <h3 className="mt-4 font-semibold text-white">
              Real-world Skills
            </h3>

            <p className="mt-2 text-sm leading-6 text-slate-400">
              Develop skills that connect directly to practical cybersecurity work.
            </p>
          </div>
        </section>

        <div className="mt-6 flex flex-col gap-2 border-t border-slate-800/60 pt-5 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2">
            <Clock3 className="h-4 w-4" />
            <span>Learning progress is saved automatically.</span>
          </div>

          <div className="flex items-center gap-2">
            <Globe className="h-4 w-4" />
            <span>Practical cybersecurity curriculum.</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LearningPage
