import { Loader2, ArrowLeft } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  startOnboarding,
  submitOnboardingAnswer,
} from '../../api/onboarding.js'

function OnboardingAssessmentPage() {
  const navigate = useNavigate()

  const [question, setQuestion] = useState(null)
  const [answers, setAnswers] = useState({})   // question_id -> [option_ids]
  const [current, setCurrent] = useState([])   // current selection
  const [progress, setProgress] = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const response = await startOnboarding()
      setQuestion(response?.data ?? response)
      setProgress((response?.data ?? response).progress)
    } catch (requestError) {
      setError(requestError?.message || 'Unable to start assessment.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  function toggleOption(optionId) {
    // Single-select by default; multi-select for goals/tools.
    const isMulti = ['goals', 'tools'].includes(question.question_id)
    if (isMulti) {
      setCurrent((prev) =>
        prev.includes(optionId)
          ? prev.filter((id) => id !== optionId)
          : [...prev, optionId],
      )
    } else {
      setCurrent([optionId])
    }
  }

  async function submit(event) {
    event.preventDefault()
    if (!current.length || submitting) return

    setSubmitting(true)
    setError('')

    const nextAnswers = {
      ...answers,
      [question.question_id]: current,
    }
    setAnswers(nextAnswers)

    try {
      // Send the answer sheet as flat strings, joined for multi-select.
      const flat = {}
      for (const [qid, ids] of Object.entries(nextAnswers)) {
        flat[qid] = ids.join(',')
      }

      const response = await submitOnboardingAnswer(
        question.question_id,
        current,
        flat,
      )
      const body = response?.data ?? response

      if (body.completed) {
        navigate('/onboarding/result', { state: { profile: body.profile } })
        return
      }

      setQuestion(body.next)
      setProgress(body.next.progress)
      setCurrent([])
    } catch (requestError) {
      setError(requestError?.message || 'Unable to submit answer.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading || !question) {
    return (
      <Page>
        <div className="flex items-center gap-3 text-sm text-slate-400">
          <Loader2 className="h-5 w-5 animate-spin text-blue-400" />
          Preparing assessment...
        </div>
      </Page>
    )
  }

  const percent = progress
    ? Math.round((progress.answered / Math.max(progress.total, 1)) * 100)
    : 0

  return (
    <Page>
      <div className="mx-auto max-w-2xl">
        <div className="mb-6 flex items-center gap-3">
          <button
            type="button"
            onClick={() => navigate('/onboarding')}
            className="text-slate-500 hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>

          <div className="flex-1">
            <div className="h-1 overflow-hidden rounded-full bg-slate-900">
              <div
                className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 transition-all"
                style={{ width: `${percent}%` }}
              />
            </div>
          </div>

          <span className="text-xs text-slate-500">
            {progress?.answered ?? 0}/{progress?.total ?? 0}
          </span>
        </div>

        <form onSubmit={submit} className="nb-card rounded-2xl p-7">
          <div className="text-[10px] font-bold uppercase tracking-[0.16em] text-blue-400">
            {question.dimension.replace(/_/g, ' ')}
          </div>

          <h1 className="mt-3 text-xl font-bold text-white">
            {question.prompt}
          </h1>

          <div className="mt-6 space-y-2">
            {question.options.map((option) => {
              const selected = current.includes(option.id)
              return (
                <button
                  type="button"
                  key={option.id}
                  onClick={() => toggleOption(option.id)}
                  className={[
                    'flex w-full items-center gap-3 rounded-xl border px-4 py-3 text-left text-sm transition',
                    selected
                      ? 'border-blue-500/60 bg-blue-500/10 text-white'
                      : 'border-slate-800 bg-slate-950/40 text-slate-300 hover:border-slate-600',
                  ].join(' ')}
                >
                  <span
                    className={[
                      'flex h-4 w-4 shrink-0 items-center justify-center rounded-full border',
                      selected
                        ? 'border-blue-400 bg-blue-400'
                        : 'border-slate-600',
                    ].join(' ')}
                  />
                  {option.label}
                </button>
              )
            })}
          </div>

          {error && (
            <div className="mt-4 rounded-xl border border-red-500/20 bg-red-500/5 p-3 text-sm text-red-300">
              {error}
            </div>
          )}

          <div className="mt-6 flex justify-end">
            <button
              type="submit"
              disabled={!current.length || submitting}
              className="nb-button-primary inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50"
            >
              {submitting && <Loader2 className="h-4 w-4 animate-spin" />}
              Continue
            </button>
          </div>
        </form>
      </div>
    </Page>
  )
}

function Page({ children }) {
  return (
    <div className="nb-page nb-grid">
      <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
        {children}
      </div>
    </div>
  )
}

export default OnboardingAssessmentPage