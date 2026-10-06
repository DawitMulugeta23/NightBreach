import {
  Loader2,
  Monitor,
  Play,
  RotateCcw,
  Square,
  Target,
  Trash2,
} from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'

import {
  getLabEnvironment,
  launchLab,
  resetEnvironment,
  startEnvironment,
  stopEnvironment,
  terminateEnvironment,
} from '../../api/labs.js'
import LabTerminal from './LabTerminal.jsx'

const RUNNING = ['ready', 'active']
const GONE = ['destroyed', 'terminating']

const storage = {
  get(key) {
    try {
      return window.localStorage.getItem(key)
    } catch {
      return null
    }
  },
  set(key, value) {
    try {
      if (value) window.localStorage.setItem(key, value)
      else window.localStorage.removeItem(key)
    } catch {
      // Storage can be unavailable; the lab still works for this page view.
    }
  },
}

function timeLeft(expiresAt, now) {
  if (!expiresAt) return null
  const seconds = Math.floor((new Date(expiresAt).getTime() - now) / 1000)
  if (seconds <= 0) return 'expired'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return hours > 0 ? `${hours}h ${minutes}m left` : `${minutes}m left`
}

/**
 * A disposable lab machine for a lesson: Start Machine, machine list,
 * terminal and controls. `children` render at the bottom of the frame, so a
 * lesson can put its required question right under the terminal.
 */
export default function LabPanel({ slug, onEnvironmentChange, children }) {
  const storageKey = `nightbreach.lab.${slug}`
  const [lab, setLab] = useState(null)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  const [now, setNow] = useState(() => Date.now())

  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 30000)
    return () => clearInterval(timer)
  }, [])

  const adopt = useCallback(
    (environment) => {
      if (!environment || GONE.includes(environment.state)) {
        storage.set(storageKey, null)
        setLab(null)
        onEnvironmentChange?.(null)
        return
      }
      storage.set(storageKey, environment.environment_id)
      setLab(environment)
      onEnvironmentChange?.(environment.environment_id)
    },
    [storageKey, onEnvironmentChange],
  )

  useEffect(() => {
    let cancelled = false
    const savedId = storage.get(storageKey)

    async function restore() {
      if (savedId) {
        try {
          const environment = await getLabEnvironment(savedId)
          if (!cancelled) adopt(environment)
        } catch {
          if (!cancelled) adopt(null)
        }
      }
      if (!cancelled) setLoading(false)
    }

    restore()
    return () => {
      cancelled = true
    }
  }, [storageKey, adopt])

  // A machine that passed its expiry is gone on the server; offer a fresh start.
  useEffect(() => {
    if (lab?.expires_at && new Date(lab.expires_at).getTime() <= now) {
      adopt(null)
    }
  }, [lab, now, adopt])

  async function run(label, action) {
    setBusy(label)
    setError('')
    try {
      await action()
    } catch (requestError) {
      setError(requestError?.message || 'The lab request failed.')
    } finally {
      setBusy('')
    }
  }

  const refresh = async (environmentId) =>
    adopt(await getLabEnvironment(environmentId))

  const launch = () =>
    run('launch', async () => adopt(await launchLab(slug)))

  const control = (label, action) => () =>
    run(label, async () => {
      await action(lab.environment_id)
      await refresh(lab.environment_id)
    })

  if (loading) {
    return (
      <div className="flex items-center gap-3 rounded-xl border border-slate-800 p-5 text-sm text-slate-500">
        <Loader2 className="h-4 w-4 animate-spin" /> Checking for a running machine...
      </div>
    )
  }

  if (!lab) {
    return (
      <div className="space-y-4">
        <div className="rounded-xl border border-slate-800 bg-slate-950/30 p-6 text-center">
          <p className="mx-auto max-w-xl text-sm text-slate-400">
            Start a private, disposable machine for this lesson. It is isolated
            from every other learner and is removed automatically when it
            expires.
          </p>
          <button
            type="button"
            onClick={launch}
            disabled={busy === 'launch'}
            className="mt-4 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition enabled:hover:bg-blue-500 disabled:opacity-60"
          >
            {busy === 'launch' ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Play className="h-4 w-4" />
            )}
            {busy === 'launch'
              ? 'Starting machine... (about 10 seconds)'
              : 'Start Machine'}
          </button>
          {error && <p className="mt-3 text-sm text-red-300">{error}</p>}
        </div>

        <div className="flex h-[200px] items-center justify-center rounded-xl border border-dashed border-slate-800 bg-[#030914] text-sm text-slate-600">
          Your terminal appears here after the machine starts.
        </div>

        {children}
      </div>
    )
  }

  const running = RUNNING.includes(lab.state)
  const attacker = lab.machines.find((machine) => machine.role === 'attack')
  const working = Boolean(busy)
  const remaining = timeLeft(lab.expires_at, now)

  return (
    <div className="space-y-4">
      <div className="space-y-4 rounded-xl border border-slate-800 bg-slate-950/30 p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="font-semibold text-white">{lab.lab_name}</div>
            <div className="mt-0.5 text-xs text-slate-500">
              {lab.network_subnet && `Network ${lab.network_subnet}`}
              {remaining && ` · ${remaining}`}
            </div>
          </div>
          <span
            className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wider ${
              running
                ? 'border-emerald-500/30 text-emerald-400'
                : 'border-orange-500/30 text-orange-400'
            }`}
          >
            {lab.state}
          </span>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          {lab.machines.map((machine) => (
            <div
              key={machine.name}
              className="flex items-start gap-3 rounded-lg border border-slate-800 p-3"
            >
              {machine.role === 'attack' ? (
                <Monitor className="mt-0.5 h-5 w-5 text-blue-400" />
              ) : (
                <Target className="mt-0.5 h-5 w-5 text-red-400" />
              )}
              <div className="min-w-0">
                <div className="text-sm font-medium text-slate-200">
                  {machine.title}
                </div>
                <div className="mt-0.5 font-mono text-xs text-slate-500">
                  {machine.address ??
                    'Address hidden: discover it by scanning the network'}
                </div>
              </div>
            </div>
          ))}
        </div>

        {lab.objectives.map((objective) => (
          <div
            key={objective.id}
            className="rounded-lg border border-blue-500/20 bg-blue-500/5 p-3"
          >
            <div className="flex justify-between text-sm font-medium text-slate-200">
              <span>{objective.title}</span>
              <span className="text-xs text-slate-500">
                {objective.points} pts
              </span>
            </div>
            <p className="mt-1 text-xs leading-5 text-slate-400">
              {objective.description}
            </p>
          </div>
        ))}

        <div className="flex flex-wrap gap-2">
          {running ? (
            <>
              <ControlButton
                onClick={control('stop', stopEnvironment)}
                disabled={working}
                icon={Square}
              >
                Stop
              </ControlButton>
              <ControlButton
                onClick={control('reset', resetEnvironment)}
                disabled={working}
                icon={RotateCcw}
              >
                Reset
              </ControlButton>
            </>
          ) : (
            <ControlButton
              onClick={control('start', startEnvironment)}
              disabled={working}
              icon={Play}
            >
              Start Machine
            </ControlButton>
          )}
          <ControlButton
            onClick={control('terminate', terminateEnvironment)}
            disabled={working}
            icon={Trash2}
          >
            End lab
          </ControlButton>
          {working && (
            <Loader2 className="h-5 w-5 animate-spin self-center text-blue-400" />
          )}
        </div>

        {error && <p className="text-sm text-red-300">{error}</p>}
      </div>

      {attacker && (
        <LabTerminal
          environmentId={lab.environment_id}
          machineName={attacker.name}
          active={running}
        />
      )}

      {children}
    </div>
  )
}

function ControlButton({ icon: Icon, children, ...props }) {
  return (
    <button
      type="button"
      {...props}
      className="inline-flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-1.5 text-sm text-slate-200 transition enabled:hover:border-slate-500 disabled:opacity-50"
    >
      <Icon className="h-4 w-4" />
      {children}
    </button>
  )
}
