import React, { useCallback, useEffect, useRef, useState } from 'react'
import toast from 'react-hot-toast'
import { arenaApi, tokenStorage } from '../utils/api'
import { useAuth } from '../context/AuthContext'
import MapBackground from '../components/MapBackground'
import Terminal from '../components/Terminal'

const STATUS_POLL_MS = 15000

function Arena() {
  const { user } = useAuth()
  const [status, setStatus] = useState(null) // { active, image, started_at }
  const [actionLoading, setActionLoading] = useState('') // '' | 'start' | 'stop'
  const [showTerminal, setShowTerminal] = useState(false)
  const [terminalKey, setTerminalKey] = useState(0)
  const pollRef = useRef(null)

  const refreshStatus = useCallback(async () => {
    const token = tokenStorage.get()
    if (!token) return
    try {
      const s = await arenaApi.getStatus(token)
      setStatus(s)
      if (!s.active) setShowTerminal(false)
      return s
    } catch {
      // keep last known status; transient network issues shouldn't blank the page
    }
  }, [])

  useEffect(() => {
    refreshStatus()
    pollRef.current = setInterval(refreshStatus, STATUS_POLL_MS)
    return () => clearInterval(pollRef.current)
  }, [refreshStatus])

  const handleStart = async () => {
    setActionLoading('start')
    try {
      await arenaApi.start(tokenStorage.get())
      await refreshStatus()
      setTerminalKey((k) => k + 1)
      setShowTerminal(true)
      toast.success('Sandbox started — connecting terminal...')
    } catch (err) {
      toast.error(err.message || 'Failed to start sandbox')
    } finally {
      setActionLoading('')
    }
  }

  const handleStop = async () => {
    setActionLoading('stop')
    try {
      await arenaApi.stop(tokenStorage.get())
      await refreshStatus()
      setShowTerminal(false)
      toast.success('Sandbox stopped')
    } catch (err) {
      toast.error(err.message || 'Failed to stop sandbox')
    } finally {
      setActionLoading('')
    }
  }

  const handleConnect = () => {
    setTerminalKey((k) => k + 1)
    setShowTerminal(true)
  }

  const active = !!status?.active

  return (
    <div className="relative w-full min-h-screen px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-8 md:py-12 overflow-hidden bg-white dark:bg-neutral-950">
      <MapBackground position="top-right" opacity={20} />

      <div className="relative max-w-7xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
              <i className="fas fa-terminal text-emerald-400 text-xl"></i>
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-neutral-900 dark:text-white">Arena</h1>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Welcome, {user?.username}. A private Linux sandbox for free exploration.
              </p>
            </div>
          </div>
        </div>

        {/* Sandbox control bar */}
        <div className="p-6 rounded-2xl bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800 mb-8">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div
                className={`w-3 h-3 rounded-full ${
                  status === null
                    ? 'bg-neutral-400'
                    : active
                      ? 'bg-emerald-400 animate-pulse'
                      : 'bg-neutral-500'
                }`}
              />
              <span className="text-sm text-neutral-900 dark:text-white">
                {status === null
                  ? 'Checking sandbox status...'
                  : active
                    ? 'Sandbox running'
                    : 'No active container'}
              </span>
              {active && status?.image && (
                <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded bg-neutral-200 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400">
                  {status.image}
                </span>
              )}
              {active && status?.started_at && (
                <span className="text-xs text-neutral-500">
                  started {new Date(status.started_at).toLocaleTimeString()}
                </span>
              )}
            </div>

            <div className="flex items-center gap-3">
              {active && !showTerminal && (
                <button
                  onClick={handleConnect}
                  className="px-5 py-2.5 rounded-lg border border-emerald-500/50 text-emerald-400 hover:bg-emerald-500/10 font-semibold text-sm transition-colors flex items-center gap-2"
                >
                  <i className="fas fa-plug"></i> Connect
                </button>
              )}
              {active ? (
                <button
                  onClick={handleStop}
                  disabled={actionLoading !== ''}
                  className="px-6 py-3 text-sm font-semibold rounded-xl bg-red-600 hover:bg-red-500 text-white transition-colors flex items-center gap-2 disabled:opacity-50"
                >
                  {actionLoading === 'stop' ? (
                    <i className="fas fa-spinner fa-spin"></i>
                  ) : (
                    <i className="fas fa-stop"></i>
                  )}
                  Stop Sandbox
                </button>
              ) : (
                <button
                  onClick={handleStart}
                  disabled={actionLoading !== ''}
                  className="btn-primary px-6 py-3 text-sm flex items-center gap-2 disabled:opacity-50"
                >
                  {actionLoading === 'start' ? (
                    <i className="fas fa-spinner fa-spin"></i>
                  ) : (
                    <i className="fas fa-play"></i>
                  )}
                  Start New Container
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Terminal area */}
        {showTerminal ? (
          <div className="h-[70vh] min-h-[480px]">
            <Terminal key={terminalKey} autoStart={true} onClose={() => setShowTerminal(false)} />
          </div>
        ) : (
          <div className="rounded-2xl bg-white dark:bg-neutral-950 border border-neutral-200 dark:border-neutral-800 overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 bg-neutral-50 dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="ml-3 text-xs text-neutral-600 dark:text-neutral-400">terminal — nightbreach</span>
            </div>
            <div className="p-10 font-mono text-sm text-neutral-500 dark:text-neutral-400 min-h-[400px] flex flex-col items-center justify-center text-center gap-4">
              <i className="fas fa-terminal text-5xl text-emerald-400/70"></i>
              {active ? (
                <>
                  <p>Sandbox is running but no terminal is attached.</p>
                  <button onClick={handleConnect} className="btn-primary px-6 py-3 text-sm flex items-center gap-2">
                    <i className="fas fa-plug"></i> Connect Terminal
                  </button>
                </>
                ) : (
                <>
                  <p>Your sandbox is not running.</p>
                  <p className="text-xs max-w-md leading-relaxed">
                    Start a container to get a private, network-isolated Linux environment with your own
                    home directory — practice commands, explore the filesystem, experiment freely.
                  </p>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Arena
