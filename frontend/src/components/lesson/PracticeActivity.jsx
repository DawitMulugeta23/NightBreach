import { CheckCircle2, Flag, Loader2, XCircle } from 'lucide-react'
import { useState } from 'react'

import {
  startPracticeAttempt,
  submitPracticeAttempt,
} from '../../services/practiceService.js'
import LabPanel from '../lab/LabPanel.jsx'
import InlinePractice from './InlinePractice.jsx'

const unwrap = (response) => response?.data ?? response

export default function PracticeActivity(props) {
  return props.activity.activity_type === 'GUIDED_CTF' ? (
    <LabActivity {...props} />
  ) : (
    <InlinePractice {...props} />
  )
}

function LabActivity({ activity, required, onSubmitted }) {
  const slug = activity.configuration?.lab_slug
  const [environmentId, setEnvironmentId] = useState(null)
  const [flag, setFlag] = useState('')
  const [busy, setBusy] = useState(false)
  const [outcome, setOutcome] = useState(null)
  const [error, setError] = useState('')

  const passed = outcome?.result === 'SUCCESS'

  async function submit(event) {
    event.preventDefault()
    if (busy || !flag.trim()) return

    setBusy(true)
    setError('')

    try {
      // The attempt is bound to this environment; the server derives the
      // expected flag from it and never from the browser.
      const attempt = unwrap(await startPracticeAttempt(activity.id, { environmentId }))
      const result = unwrap(await submitPracticeAttempt(attempt.id, flag.trim()))
      setOutcome(result)
      await onSubmitted?.(result)
    } catch (requestError) {
      setError(requestError?.message || 'Unable to submit the flag.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="space-y-4 rounded-2xl border border-blue-500/20 bg-blue-500/[0.03] p-5 sm:p-6">
      <div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider text-blue-400">
        <Flag className="h-4 w-4" />
        Practical lab
        {required && (
          <span className="rounded border border-orange-500/30 px-1.5 py-0.5 text-[10px] text-orange-400">
            Required
          </span>
        )}
      </div>

      <div>
        <h3 className="text-lg font-semibold text-white">{activity.title}</h3>
        {activity.instructions && (
          <p className="mt-1 text-sm text-slate-500">{activity.instructions}</p>
        )}
      </div>

      {slug ? (
        <LabPanel slug={slug} onEnvironmentChange={setEnvironmentId} />
      ) : (
        <p className="rounded-lg border border-orange-500/30 bg-orange-500/5 p-3 text-sm text-orange-300">
          This activity has no lab attached.
        </p>
      )}

      <form onSubmit={submit} className="flex flex-wrap gap-2">
        <input
          value={flag}
          onChange={(event) => setFlag(event.target.value)}
          disabled={busy || passed}
          placeholder="NB{...}"
          className="min-w-0 flex-1 rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 font-mono text-sm text-slate-200 outline-none focus:border-blue-500/60"
        />
        <button
          type="submit"
          disabled={busy || passed || !environmentId || !flag.trim()}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white transition enabled:hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {busy && <Loader2 className="h-4 w-4 animate-spin" />}
          Submit Flag
        </button>
      </form>

      {error && <p className="text-sm text-red-300">{error}</p>}

      {outcome && (
        <div
          className={`flex items-center gap-3 rounded-xl border p-4 ${
            passed ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-red-500/30 bg-red-500/5'
          }`}
        >
          {passed ? (
            <CheckCircle2 className="h-6 w-6 text-emerald-400" />
          ) : (
            <XCircle className="h-6 w-6 text-red-400" />
          )}
          <div className="font-semibold text-white">
            {passed ? 'Flag accepted. Lab complete.' : 'That is not the right flag. Keep investigating.'}
          </div>
        </div>
      )}
    </section>
  )
}
