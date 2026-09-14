import React from 'react'
import MapBackground from '../components/MapBackground'

function Leaderboard() {
  const rankings = [
    { rank: 1, username: 'Coming Soon', levels: 0, score: 0, medal: '🥇' },
    { rank: 2, username: 'Coming Soon', levels: 0, score: 0, medal: '🥈' },
    { rank: 3, username: 'Coming Soon', levels: 0, score: 0, medal: '🥉' },
  ]

  return (
    <div className="relative w-full min-h-screen px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-8 md:py-12 overflow-hidden bg-white dark:bg-neutral-950">
      <MapBackground position="top-right" opacity={20} />

      <div className="relative max-w-7xl mx-auto">
        <h1 className="text-xl md:text-2xl lg:text-3xl font-bold text-neutral-900 dark:text-white mb-2">
          <i className="fas fa-trophy text-emerald-400 mr-3"></i>LEADERBOARD
        </h1>
        <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-8 md:mb-10">
          <i className="fas fa-users text-emerald-400 mr-2"></i>
          Top performers in the NightBreach community.
        </p>

        <div className="rounded-2xl bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800 overflow-hidden">
          <div className="grid grid-cols-4 gap-4 p-4 md:p-6 border-b border-neutral-200 dark:border-neutral-800 text-xs font-semibold uppercase tracking-wider text-neutral-600 dark:text-neutral-400">
            <div><i className="fas fa-hashtag mr-1"></i>Rank</div>
            <div><i className="fas fa-user mr-1"></i>Username</div>
            <div><i className="fas fa-check-circle mr-1"></i>Levels</div>
            <div><i className="fas fa-star mr-1"></i>Score</div>
          </div>
          <div className="divide-y divide-neutral-200 dark:divide-neutral-800">
            {rankings.map((r) => (
              <div key={r.rank} className="grid grid-cols-4 gap-4 p-4 md:p-6 text-sm text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800/50 transition-colors">
                <div className="text-emerald-400 font-bold">{r.medal} #{r.rank}</div>
                <div>{r.username}</div>
                <div>{r.levels}</div>
                <div>{r.score}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Leaderboard
