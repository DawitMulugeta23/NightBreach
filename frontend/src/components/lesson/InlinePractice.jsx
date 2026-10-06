import {
  CheckCircle2,
  ClipboardCheck,
  Loader2,
  RotateCcw,
  Send,
  XCircle,
} from 'lucide-react'
import { useState } from 'react'

import {
  startPracticeAttempt,
  submitPracticeAttempt,
} from '../../services/practiceService.js'

const unwrap = (response) => response?.data ?? response
const PASS_RESULTS = ['PASSED', 'PASS', 'CORRECT', 'SUCCESS']

function normalizeOption(option) {
  if (typeof option === 'string') {
    return { value: option, label: option }
  }

  const label = option?.label ?? option?.text ?? option?.value ?? ''
  return { value: String(option?.value ?? label), label: String(label) }
}

export default function InlinePractice({
  activity,
  required,
  onSubmitted,
}) {
  const rawOptions = activity.configuration?.options ?? activity.configuration?.choices
  const options = Array.isArray(rawOptions)
    ? rawOptions.map(normalizeOption)
    : null
  const isChoice =
    Boolean(options) &&
    String(activity.evaluation_type || '').includes('CHOICE')

  const [answer, setAnswer] = useState('')
  const [busy, setBusy] = useState(false)
  const [outcome, setOutcome] = useState(null)
  const [error, setError] = useState('')

  const passed =
    outcome &&
    PASS_RESULTS.includes(String(outcome.result || '').toUpperCase())

  async function handleSubmit(event) {
    event.preventDefault()
    if (busy || !answer.trim()) return

    setBusy(true)
    setError('')

    try {
      // One attempt per submission; the backend evaluates, never the browser.
      const attempt = unwrap(await startPracticeAttempt(activity.id))
      const result = unwrap(
        await submitPracticeAttempt(attempt.id, answer.trim()),
      )

      setOutcome(result)
      await onSubmitted?.(result)
    } catch (requestError) {
      setError(requestError?.message || 'Unable to submit your answer.')
    } finally {
      setBusy(false)
    }
  }

  function retry() {
    setOutcome(null)
    setAnswer('')
    setError('')
  }

  const locked = busy || Boolean(outcome)

  return (
    <section className="rounded-2xl border border-blue-500/20 bg-blue-500/[0.03] p-5 sm:p-6">
      <div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider text-blue-400">
        <ClipboardCheck className="h-4 w-4" />
        Practice
        {required && (
          <span className="rounded border border-orange-500/30 px-1.5 py-0.5 text-[10px] text-orange-400">
            Required
          </span>
        )}
      </div>

      <h3 className="mt-3 text-lg font-semibold text-white">
        {activity.title}
      </h3>

      {activity.instructions && (
        <p className="mt-1 text-sm text-slate-500">{activity.instructions}</p>
      )}

      <form onSubmit={handleSubmit} className="mt-4">
        {isChoice ? (
          <fieldset disabled={locked} className="space-y-2">
            <legend className="sr-only">{activity.title}</legend>
            {options.map((option) => {
              const selected = answer === option.value
              return (
                <label
                  key={option.value}
                  className={`flex cursor-pointer items-center gap-3 rounded-xl border px-4 py-3 text-sm transition ${
                    selected
                      ? 'border-blue-500/60 bg-blue-500/10 text-white'
                      : 'border-slate-800 bg-slate-950/40 text-slate-300 hover:border-slate-600'
                  } ${locked ? 'cursor-not-allowed opacity-70' : ''}`}
                >
                  <input
                    type="radio"
                    name={`activity-${activity.id}`}
                    value={option.value}
                    checked={selected}
                    onChange={() => setAnswer(option.value)}
                    className="h-4 w-4 accent-blue-500"
                  />
                  {option.label}
                </label>
              )
            })}
          </fieldset>
        ) : (
          <textarea
            value={answer}
            onChange={(event) => setAnswer(event.target.value)}
            disabled={locked}
            rows={3}
            placeholder="Enter your answer..."
            className="w-full resize-y rounded-xl border border-slate-800 bg-slate-950/60 p-3 font-mono text-sm text-slate-200 outline-none focus:border-blue-500/60"
          />
        )}

        {error && (
          <p className="mt-3 rounded-lg border border-red-500/20 bg-red-500/5 p-3 text-sm text-red-300">
            {error}
          </p>
        )}

        {outcome ? (
          <div
            className={`mt-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border p-4 ${
              passed
                ? 'border-emerald-500/30 bg-emerald-500/5'
                : 'border-red-500/30 bg-red-500/5'
            }`}
          >
            <div className="flex items-center gap-3">
              {passed ? (
                <CheckCircle2 className="h-6 w-6 text-emerald-400" />
              ) : (
                <XCircle className="h-6 w-6 text-red-400" />
              )}
              <div>
                <div className="font-semibold text-white">
                  {passed ? 'Correct' : 'Not quite'}
                </div>
                <div className="text-xs text-slate-500">
                  Attempt {outcome.attempt_no}
                  {outcome.score != null && ` · Score ${outcome.score}`}
                </div>
              </div>
            </div>

            {!passed && (
              <button
                type="button"
                onClick={retry}
                className="inline-flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-1.5 text-sm text-slate-200 transition hover:border-slate-500"
              >
                <RotateCcw className="h-4 w-4" />
                Try again
              </button>
            )}
          </div>
        ) : (
          <div className="mt-4 flex justify-end">
            <button
              type="submit"
              disabled={busy || !answer.trim()}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition enabled:hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {busy ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              Submit Answer
            </button>
          </div>
        )}
      </form>
    </section>
  )
}
