import React from 'react'
import { useAuth } from '../context/AuthContext'
import MapBackground from '../components/MapBackground'

function Arena() {
  const { user } = useAuth()

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
              <p className="text-sm text-neutral-600 dark:text-neutral-400">Welcome, {user?.username}. Ready to hack?</p>
            </div>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800 mb-8">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-yellow-400 animate-pulse"></div>
              <span className="text-sm text-neutral-300">No active container</span>
            </div>
            <button className="btn-primary px-6 py-3 text-sm flex items-center gap-2">
              <i className="fas fa-play"></i> Start New Container
            </button>
          </div>
        </div>

        <div className="rounded-2xl bg-white dark:bg-neutral-950 border border-neutral-200 dark:border-neutral-800 overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 bg-neutral-50 dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="ml-3 text-xs text-neutral-600 dark:text-neutral-400">terminal — nightbreach</span>
          </div>
          <div className="p-6 font-mono text-sm text-emerald-400 min-h-[400px]">
            <p>$ Welcome to NightBreach Terminal</p>
            <p>$ Login successful as {user?.username}</p>
            <p>$ Type 'help' for available commands</p>
            <p>$ <span className="animate-pulse">_</span></p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Arena
