import {
  ArrowLeft,
  CheckCircle2,
  Loader2,
  Send,
  Terminal,
  XCircle,
} from 'lucide-react'
import {
  useEffect,
  useMemo,
  useState,
} from 'react'
import {
  useLocation,
  useNavigate,
  useParams,
} from 'react-router-dom'

import StatusBadge from '../../components/common/StatusBadge.jsx'
import {
  startPracticeAttempt,
  submitPracticeAttempt,
} from '../../services/practiceService.js'

function PracticePage() {
  const { activityId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()

  const activity =
    location.state?.activity || null

  const practice =
    location.state?.practice || null

  const lessonId =
    location.state?.lessonId || null

  const [attempt, setAttempt] = useState(null)
  const [answer, setAnswer] = useState('')
  const [starting, setStarting] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const configuration = useMemo(() => {
    if (
      activity?.configuration &&
      typeof activity.configuration ===
        'object'
    ) {
      return activity.configuration
    }

    return {}
  }, [activity])

  useEffect(() => {
    if (!activity) {
      return
    }

    let cancelled = false

    async function initialize() {
      setStarting(true)
      setError('')

      try {
        const response =
          await startPracticeAttempt(
            activityId,
          )

        if (!cancelled) {
          setAttempt(
            response?.data ?? response,
          )
        }
      } catch (requestError) {
        if (!cancelled) {
          setError(
            requestError?.message ||
              'Unable to start the practice attempt.',
          )
        }
      } finally {
        if (!cancelled) {
          setStarting(false)
        }
      }
    }

    initialize()

    return () => {
      cancelled = true
    }
  }, [activity, activityId])

  if (!activity) {
    return (
      <Shell>
        <div className="mx-auto max-w-xl py-20 text-center">
          <Terminal className="mx-auto h-8 w-8 text-slate-600" />

          <h1 className="mt-5 text-xl font-bold text-white">
            Practice context unavailable
          </h1>

          <p className="mt-2 text-sm leading-6 text-slate-500">
            Open this activity from its lesson so NightBreach can load the activity configuration.
          </p>

          <button
            type="button"
            onClick={() =>
              navigate(
                lessonId
                  ? `/lessons/${lessonId}`
                  : '/learning',
              )
            }
            className="nb-button-secondary mt-6 rounded-xl px-4 py-2.5 text-sm font-semibold"
          >
            Return to Lesson
          </button>
        </div>
      </Shell>
    )
  }

  const result =
    attempt?.result || null

  const submitted =
    Boolean(attempt?.submitted_at) ||
    Boolean(result)

  async function handleSubmit(event) {
    event.preventDefault()

    if (!attempt?.id || !answer.trim()) {
      return
    }

    setSubmitting(true)
    setError('')

    try {
      const response =
        await submitPracticeAttempt(
          attempt.id,
          answer.trim(),
        )

      setAttempt(
        response?.data ?? response,
      )
    } catch (requestError) {
      setError(
        requestError?.message ||
          'Unable to submit the practice answer.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Shell>
      <button
        type="button"
        onClick={() =>
          navigate(
            lessonId
              ? `/lessons/${lessonId}`
              : '/learning',
            {
              state: {
                fromPractice: submitted,
              },
            },
          )
        }
        className="mb-5 inline-flex items-center gap-2 text-sm text-slate-500 transition hover:text-white"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Lesson
      </button>

      <div className="mx-auto max-w-4xl">
        <div className="nb-card overflow-hidden rounded-2xl">
          <div className="border-b border-slate-800/80 p-6">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <Terminal className="h-5 w-5 text-blue-400" />

                  <span className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-600">
                    {activity.activity_type}
                  </span>
                </div>

                <h1 className="mt-3 text-2xl font-bold tracking-tight text-white">
                  {activity.title}
                </h1>

                {practice?.title && (
                  <p className="mt-2 text-sm text-slate-500">
                    {practice.title}
                  </p>
                )}
              </div>

              <StatusBadge
                tone={
                  submitted
                    ? result === 'PASSED'
                      ? 'green'
                      : 'red'
                    : 'blue'
                }
              >
                {submitted
                  ? result || 'Submitted'
                  : 'Attempt'}
              </StatusBadge>
            </div>
          </div>

          <div className="p-6">
            {activity.instructions && (
              <div className="rounded-xl border border-slate-800 bg-slate-950/30 p-5">
                <div className="text-[10px] font-bold uppercase tracking-wider text-slate-600">
                  Instructions
                </div>

                <div className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-300">
                  {activity.instructions}
                </div>
              </div>
            )}

            <ConfigurationView
              configuration={configuration}
            />

            {error && (
              <div className="mt-5 rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-300">
                {error}
              </div>
            )}

            {starting ? (
              <div className="flex items-center justify-center py-12 text-sm text-slate-500">
                <Loader2 className="mr-3 h-5 w-5 animate-spin text-blue-400" />
                Starting attempt...
              </div>
            ) : submitted ? (
              <ResultView
                result={result}
                score={attempt?.score}
              />
            ) : (
              <form
                onSubmit={handleSubmit}
                className="mt-6"
              >
                <label
                  htmlFor="practice-answer"
                  className="text-xs font-semibold uppercase tracking-wider text-slate-500"
                >
                  Your submission
                </label>

                <textarea
                  id="practice-answer"
                  value={answer}
                  onChange={(event) =>
                    setAnswer(
                      event.target.value,
                    )
                  }
                  disabled={submitting}
                  rows={7}
                  placeholder="Enter your answer..."
                  className="nb-input mt-2 w-full resize-y rounded-xl p-4 text-sm leading-6"
                />

                <div className="mt-4 flex justify-end">
                  <button
                    type="submit"
                    disabled={
                      submitting ||
                      !answer.trim()
                    }
                    className="nb-button-primary inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {submitting ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}

                    Submit Answer
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      </div>
    </Shell>
  )
}

function ConfigurationView({
  configuration,
}) {
  const question =
    configuration.question ||
    configuration.prompt

  const options =
    configuration.options ||
    configuration.choices

  if (!question && !Array.isArray(options)) {
    return null
  }

  return (
    <div className="mt-5 rounded-xl border border-blue-500/10 bg-blue-500/5 p-5">
      {question && (
        <div className="text-sm leading-7 text-slate-200">
          {question}
        </div>
      )}

      {Array.isArray(options) && (
        <div className="mt-4 space-y-2">
          {options.map((option, index) => {
            const value =
              typeof option === 'string'
                ? option
                : option?.label ||
                  option?.text ||
                  option?.value ||
                  JSON.stringify(
                    option,
                  )

            return (
              <div
                key={`${value}-${index}`}
                className="rounded-lg border border-slate-800 bg-slate-950/40 px-4 py-3 text-sm text-slate-300"
              >
                {value}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

function ResultView({
  result,
  score,
}) {
  const passed =
    String(result || '').toUpperCase() ===
    'PASSED'

  return (
    <div
      className={[
        'mt-6 rounded-2xl border p-6',
        passed
          ? 'border-emerald-500/20 bg-emerald-500/5'
          : 'border-red-500/20 bg-red-500/5',
      ].join(' ')}
    >
      <div className="flex items-center gap-3">
        {passed ? (
          <CheckCircle2 className="h-7 w-7 text-emerald-400" />
        ) : (
          <XCircle className="h-7 w-7 text-red-400" />
        )}

        <div>
          <h2 className="font-bold text-white">
            {result || 'Submission processed'}
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            The backend has evaluated your submission.
          </p>
        </div>
      </div>

      {score !== null &&
        score !== undefined && (
          <div className="mt-5 border-t border-slate-800/70 pt-4">
            <span className="text-xs text-slate-600">
              Score
            </span>

            <div className="mt-1 text-2xl font-bold text-white">
              {score}
            </div>
          </div>
        )}
    </div>
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

export default PracticePage
