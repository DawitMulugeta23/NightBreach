import {
  ArrowLeft,
  ChevronRight,
  Lock,
  Loader2,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import {
  useNavigate,
  useParams,
} from 'react-router-dom'

import SectionHeader from '../../components/common/SectionHeader.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import { getRoom } from '../../services/learningService.js'
import {
  getRoomProgress,
  getLessonProgress,
} from '../../services/progressService.js'

function RoomPage() {
  const { roomId } = useParams()
  const navigate = useNavigate()

  const [room, setRoom] = useState(null)
  const [progress, setProgress] = useState(null)
  const [lessonProgress, setLessonProgress] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function initialize() {
      setLoading(true)
      setError('')

      try {
        const [roomResponse, progressResponse] =
          await Promise.all([
            getRoom(roomId),
            getRoomProgress(roomId).catch(
              () => null,
            ),
          ])

        if (cancelled) {
          return
        }

        const roomData =
          roomResponse?.data ?? roomResponse

        setRoom(roomData)

        setProgress(
          progressResponse?.data ??
            progressResponse,
        )

        const lessons =
          Array.isArray(roomData?.lessons)
            ? roomData.lessons
            : []

        const entries = await Promise.all(
          lessons.map(async (lesson) => {
            try {
              const response =
                await getLessonProgress(lesson.id)

              return [
                lesson.id,
                response?.data ?? response,
              ]
            } catch {
              return [lesson.id, null]
            }
          }),
        )

        if (!cancelled) {
          setLessonProgress(
            Object.fromEntries(entries),
          )
        }
      } catch (requestError) {
        if (!cancelled) {
          setError(
            requestError?.message ||
              'Unable to load this room.',
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
  }, [roomId])

  if (loading) {
    return <LoadingState />
  }

  if (error || !room) {
    return (
      <Shell>
        <ErrorState
          message={error || 'Room not found.'}
        />
      </Shell>
    )
  }

  const status =
    progress?.status || 'NOT_STARTED'

  const lessons = Array.isArray(room.lessons)
    ? room.lessons
    : []

  return (
    <Shell>
      <button
        type="button"
        onClick={() =>
          navigate(
            `/modules/${room.module_id}`,
          )
        }
        className="mb-5 inline-flex items-center gap-2 text-sm text-slate-500 transition hover:text-white"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Module
      </button>

      <SectionHeader
        eyebrow="Room"
        title={room.title}
        description={room.description}
      />

      <div className="mt-6 flex flex-wrap items-center gap-3">
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

        <span className="rounded-md border border-slate-800 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
          {room.access_level}
        </span>

        <span className="text-xs text-slate-600">
          {lessons.length} lesson
          {lessons.length === 1 ? '' : 's'}
        </span>
      </div>

      <section className="mt-7">
        <div className="mb-4">
          <h2 className="text-lg font-bold text-white">
            Lessons
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Complete the lessons and required activities in order.
          </p>
        </div>

        <div className="space-y-3">
          {lessons.map((lesson, index) => {
            const lessonState =
              lessonProgress[lesson.id]

            const lessonStatus =
              lessonState?.status ||
              'NOT_STARTED'

            const locked =
              room.access_level === 'PRO' &&
              lesson.access_override === 'PRO'

            return (
              <button
                key={lesson.id}
                type="button"
                onClick={() => {
                  if (!locked) {
                    navigate(
                      `/lessons/${lesson.id}`,
                    )
                  }
                }}
                disabled={locked}
                className={[
                  'nb-card flex w-full items-center gap-4 rounded-xl p-4 text-left transition',
                  locked
                    ? 'cursor-not-allowed opacity-60'
                    : 'nb-card-hover',
                ].join(' ')}
              >
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-blue-500/20 bg-blue-500/10 text-sm font-bold text-blue-400">
                  {index + 1}
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-semibold text-white">
                      {lesson.title}
                    </h3>

                    {lessonStatus ===
                      'COMPLETED' && (
                      <StatusBadge tone="green">
                        Completed
                      </StatusBadge>
                    )}

                    {lessonStatus ===
                      'IN_PROGRESS' && (
                      <StatusBadge tone="blue">
                        In Progress
                      </StatusBadge>
                    )}
                  </div>

                  <p className="mt-1 line-clamp-2 text-sm text-slate-500">
                    {lesson.description}
                  </p>
                </div>

                {locked ? (
                  <Lock className="h-5 w-5 shrink-0 text-slate-600" />
                ) : (
                  <ChevronRight className="h-5 w-5 shrink-0 text-slate-600" />
                )}
              </button>
            )
          })}

          {lessons.length === 0 && (
            <div className="rounded-xl border border-slate-800/70 p-8 text-center text-sm text-slate-500">
              No lessons are currently available in this room.
            </div>
          )}
        </div>
      </section>
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

function LoadingState() {
  return (
    <Shell>
      <div className="flex min-h-[500px] items-center justify-center text-sm text-slate-400">
        <Loader2 className="mr-3 h-5 w-5 animate-spin text-blue-400" />
        Loading room...
      </div>
    </Shell>
  )
}

function ErrorState({ message }) {
  return (
    <div className="flex min-h-[500px] items-center justify-center">
      <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-6 text-center">
        <p className="text-sm text-red-300">
          {message}
        </p>
      </div>
    </div>
  )
}

export default RoomPage
