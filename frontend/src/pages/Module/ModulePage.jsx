import {
  ArrowLeft,
  BookOpen,
  ChevronRight,
  Layers3,
  Loader2,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import {
  useNavigate,
  useParams,
} from 'react-router-dom'

import SectionHeader from '../../components/common/SectionHeader.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import { getModule } from '../../services/learningService.js'
import { getModuleProgress } from '../../services/progressService.js'

function ModulePage() {
  const { moduleId } = useParams()
  const navigate = useNavigate()

  const [module, setModule] = useState(null)
  const [progress, setProgress] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function initialize() {
      setLoading(true)
      setError('')

      try {
        const [moduleResponse, progressResponse] =
          await Promise.all([
            getModule(moduleId),
            getModuleProgress(moduleId).catch(
              () => null,
            ),
          ])

        if (cancelled) {
          return
        }

        setModule(
          moduleResponse?.data ?? moduleResponse,
        )

        setProgress(
          progressResponse?.data ??
            progressResponse,
        )
      } catch (requestError) {
        if (!cancelled) {
          setError(
            requestError?.message ||
              'Unable to load this module.',
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
  }, [moduleId])

  if (loading) {
    return <Loading />
  }

  if (error || !module) {
    return (
      <Shell>
        <ErrorMessage message={error || 'Module not found.'} />
      </Shell>
    )
  }

  const status =
    progress?.status || 'NOT_STARTED'

  return (
    <Shell>
      <button
        type="button"
        onClick={() =>
          navigate(
            `/learning-paths/${module.learning_path_id}`,
          )
        }
        className="mb-5 inline-flex items-center gap-2 text-sm text-slate-500 hover:text-white"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Learning Path
      </button>

      <SectionHeader
        eyebrow="Module"
        title={module.title}
        description={module.description}
      />

      <div className="mt-6 flex items-center gap-3">
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

        <span className="text-xs text-slate-600">
          Module {module.position + 1}
        </span>
      </div>

      <section className="mt-6">
        <div className="mb-4 flex items-center gap-2">
          <Layers3 className="h-5 w-5 text-blue-400" />

          <h2 className="text-lg font-bold text-white">
            Rooms
          </h2>
        </div>

        <div className="space-y-3">
          {(module.rooms || []).map((room, index) => (
            <button
              key={room.id}
              type="button"
              onClick={() => navigate(`/rooms/${room.id}`)}
              className="nb-card nb-card-hover flex w-full items-center gap-4 rounded-xl p-4 text-left"
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-purple-500/20 bg-purple-500/10 text-sm font-bold text-purple-400">
                {index + 1}
              </div>

              <div className="min-w-0 flex-1">
                <h3 className="font-semibold text-white">
                  {room.title}
                </h3>

                <p className="mt-1 line-clamp-2 text-sm text-slate-500">
                  {room.description}
                </p>
              </div>

              <div className="flex items-center gap-3">
                <span className="hidden rounded-md border border-slate-800 px-2 py-1 text-[10px] font-semibold text-slate-500 sm:inline">
                  {room.access_level}
                </span>

                <ChevronRight className="h-5 w-5 text-slate-600" />
              </div>
            </button>
          ))}

          {module.rooms?.length === 0 && (
            <div className="rounded-xl border border-slate-800/70 p-8 text-center text-sm text-slate-500">
              No rooms are currently available in this module.
            </div>
          )}
        </div>
      </section>

      <div className="mt-6 rounded-xl border border-slate-800/60 bg-slate-950/20 p-4 text-xs text-slate-600">
        <BookOpen className="mr-2 inline h-4 w-4" />
        Complete the lessons and required practice inside the rooms to
        advance your learning progress.
      </div>
    </Shell>
  )
}

function Shell({ children }) {
  return (
    <div className="nb-page nb-grid">
      <div className="mx-auto max-w-[1200px] px-4 py-6 sm:px-6 lg:px-8">
        {children}
      </div>
    </div>
  )
}

function Loading() {
  return (
    <Shell>
      <div className="flex min-h-[500px] items-center justify-center text-sm text-slate-400">
        <Loader2 className="mr-3 h-5 w-5 animate-spin text-blue-400" />
        Loading module...
      </div>
    </Shell>
  )
}

function ErrorMessage({ message }) {
  return (
    <div className="flex min-h-[500px] items-center justify-center">
      <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-6 text-center">
        <p className="text-sm text-red-300">{message}</p>
      </div>
    </div>
  )
}

export default ModulePage
