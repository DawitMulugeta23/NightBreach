import {
  ArrowLeft,
  ArrowRight,
  Loader2,
  Lock,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import {
  useLocation,
  useNavigate,
  useParams,
} from 'react-router-dom'

import StatusBadge from '../../components/common/StatusBadge.jsx'
import LessonBlocks from '../../components/lesson/LessonBlocks.jsx'
import PracticeActivity from '../../components/lesson/PracticeActivity.jsx'
import RoomNav from '../../components/lesson/RoomNav.jsx'
import * as learningService from '../../services/learningService.js'
import { getLessonCompletionState } from '../../services/progressService.js'

const unwrap = (response) => response?.data ?? response

function LessonPage() {
  const { lessonId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()

  const [lesson, setLesson] = useState(null)
  const [completion, setCompletion] = useState(null)
  const [room, setRoom] = useState(null)
  const [siblingStatus, setSiblingStatus] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Lesson + its completion state (backend is authoritative).
  useEffect(() => {
    let cancelled = false

    async function load() {
      setLoading(true)
      setError('')

      try {
        const [lessonResponse, completionResponse] = await Promise.all([
          learningService.getLesson(lessonId),
          getLessonCompletionState(lessonId).catch(() => null),
        ])

        if (cancelled) return
        setLesson(unwrap(lessonResponse))
        setCompletion(unwrap(completionResponse))
      } catch (requestError) {
        if (!cancelled) {
          setError(requestError?.message || 'Unable to load this lesson.')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [lessonId])

  // Refresh after returning from a practice attempt.
  useEffect(() => {
    if (!location.state?.fromPractice) return
    let cancelled = false

    getLessonCompletionState(lessonId)
      .then((response) => {
        if (!cancelled) setCompletion(unwrap(response))
      })
      .catch(() => {})

    return () => {
      cancelled = true
    }
  }, [lessonId, location.state?.fromPractice])

  // Room navigation: sibling lessons and their statuses.
  const roomId = lesson?.room_id
  useEffect(() => {
    if (!roomId || typeof learningService.getRoom !== 'function') return
    let cancelled = false

    learningService
      .getRoom(roomId)
      .then(async (response) => {
        const roomData = unwrap(response)
        if (cancelled) return
        setRoom(roomData)

        const siblings = Array.isArray(roomData?.lessons)
          ? roomData.lessons
          : []

        const entries = await Promise.all(
          siblings.map(async (item) => {
            const state = await getLessonCompletionState(item.id).catch(
              () => null,
            )
            return [item.id, unwrap(state)?.lesson_status || 'NOT_STARTED']
          }),
        )

        if (!cancelled) setSiblingStatus(Object.fromEntries(entries))
      })
      .catch(() => {})

    return () => {
      cancelled = true
    }
  }, [roomId])

  async function handlePracticeSubmitted() {
    const state = await getLessonCompletionState(lessonId).catch(() => null)
    const data = unwrap(state)
    if (data) {
      setCompletion(data)
      setSiblingStatus((current) => ({
        ...current,
        [lessonId]: data.lesson_status,
      }))
    }
  }

  if (loading) return <LoadingState />

  if (error || !lesson) {
    return (
      <Shell>
        <ErrorState message={error || 'Lesson not found.'} />
      </Shell>
    )
  }

  const lessonStatus = completion?.lesson_status || 'NOT_STARTED'
  const statusFor = (id) =>
    id === lessonId ? lessonStatus : siblingStatus[id] || 'NOT_STARTED'

  const blocks = Array.isArray(lesson.content_blocks)
    ? lesson.content_blocks
    : []
  const lessonPractices = (
    Array.isArray(lesson.lesson_practices) ? lesson.lesson_practices : []
  )
    .slice()
    .sort((a, b) => (a.position ?? 0) - (b.position ?? 0))

  const roomLessons = (Array.isArray(room?.lessons) ? room.lessons : [])
    .slice()
    .sort((a, b) => (a.position ?? 0) - (b.position ?? 0))
  const index = roomLessons.findIndex((item) => item.id === lessonId)
  const previous = index > 0 ? roomLessons[index - 1] : null
  const next =
    index >= 0 && index < roomLessons.length - 1
      ? roomLessons[index + 1]
      : null

  const gated =
    lesson.completion_rule === 'REQUIRED_PRACTICE' &&
    lessonStatus !== 'COMPLETED'

  return (
    <Shell>
      <header className="mb-6">
        <button
          type="button"
          onClick={() => navigate(`/rooms/${lesson.room_id}`)}
          className="mb-3 inline-flex items-center gap-2 text-sm text-slate-500 transition hover:text-white"
        >
          <ArrowLeft className="h-4 w-4" />
          {room?.title || 'Back to Room'}
        </button>

        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-3xl font-bold text-white">{lesson.title}</h1>
          <StatusBadge
            tone={
              lessonStatus === 'COMPLETED'
                ? 'green'
                : lessonStatus === 'IN_PROGRESS'
                  ? 'blue'
                  : 'gray'
            }
          >
            {lessonStatus === 'COMPLETED'
              ? 'Completed'
              : lessonStatus === 'IN_PROGRESS'
                ? 'In Progress'
                : 'Not Started'}
          </StatusBadge>
        </div>

        {lesson.description && (
          <p className="mt-2 max-w-2xl text-slate-500">
            {lesson.description}
          </p>
        )}
      </header>

      <div className="grid gap-6 lg:grid-cols-[260px_minmax(0,1fr)]">
        <aside>
          {roomLessons.length > 0 && (
            <RoomNav
              roomTitle={room?.title}
              lessons={roomLessons}
              currentId={lessonId}
              statusFor={statusFor}
              onSelect={(id) => navigate(`/lessons/${id}`)}
            />
          )}
        </aside>

        <main className="min-w-0">
          {blocks.length > 0 ? (
            <LessonBlocks blocks={blocks} />
          ) : (
            <p className="text-sm text-slate-500">
              This lesson does not have content blocks yet.
            </p>
          )}

          <section className="mt-8 space-y-4">
            {lessonPractices.length > 0 && (
              <h2 className="text-xl font-bold text-white">Practice</h2>
            )}

            {lessonPractices.flatMap((lessonPractice) =>
              (lessonPractice.practice?.activities ?? []).map((activity) => (
                <PracticeActivity
                  key={activity.id}
                  activity={activity}
                  required={lessonPractice.required}
                  onSubmitted={handlePracticeSubmitted}
                />
              )),
            )}

            {lessonPractices.length === 0 && (
              <p className="text-xs text-slate-600">
                No practice activities are attached to this lesson yet.
              </p>
            )}
          </section>

          {location.state?.fromPractice && (
            <div className="mt-4 rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 text-sm text-emerald-300">
              Practice result updated. Lesson progress has been refreshed.
            </div>
          )}

          <footer className="mt-6 flex items-center justify-between gap-4">
            <button
              type="button"
              disabled={!previous}
              onClick={() => previous && navigate(`/lessons/${previous.id}`)}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-800 px-4 py-2 text-sm text-slate-300 transition enabled:hover:border-slate-600 disabled:opacity-40"
            >
              <ArrowLeft className="h-4 w-4" />
              Previous
            </button>

            <div className="flex items-center gap-3">
              {gated && next && (
                <span className="hidden items-center gap-1.5 text-xs text-orange-400 sm:inline-flex">
                  <Lock className="h-3.5 w-3.5" />
                  Complete the required practice to continue
                </span>
              )}

              <button
                type="button"
                disabled={!next || gated}
                onClick={() => next && navigate(`/lessons/${next.id}`)}
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition enabled:hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Next lesson
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </footer>
        </main>
      </div>
    </Shell>
  )
}

function Shell({ children }) {
  return (
    <div className="nb-page nb-grid">
      <div className="mx-auto max-w-[1280px] px-4 py-6 sm:px-6 lg:px-8">
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
        Loading lesson...
      </div>
    </Shell>
  )
}

function ErrorState({ message }) {
  return (
    <div className="flex min-h-[500px] items-center justify-center">
      <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-6 text-center">
        <p className="text-sm text-red-300">{message}</p>
      </div>
    </div>
  )
}

export default LessonPage
