import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'
import MapBackground from '../components/MapBackground'
import { learningApi, tokenStorage } from '../utils/api'

function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = tokenStorage.get()
    if (!token) {
      setLoading(false)
      return
    }
    learningApi.getStats(token)
      .then(setStats)
      .catch(() => toast.error('Could not load dashboard stats.'))
      .finally(() => setLoading(false))
  }, [])

  const statCards = [
    { icon: 'fa-flag', label: 'Levels Completed', value: stats?.levels_completed ?? 0, color: 'text-emerald-400' },
    { icon: 'fa-book-open', label: 'Lessons Completed', value: stats?.lessons_completed ?? 0, color: 'text-blue-400' },
    { icon: 'fa-star', label: 'Total Score', value: stats?.total_score ?? 0, color: 'text-yellow-400' },
    { icon: 'fa-circle-question', label: 'Questions Answered', value: stats?.questions_answered ?? 0, color: 'text-purple-400' },
  ]

  return (
    <div className="relative w-full min-h-screen px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-8 md:py-12 overflow-hidden bg-white dark:bg-neutral-950">
      <MapBackground position="top-right" opacity={20} />

      <div className="relative max-w-7xl mx-auto">
        <div className="mb-8 md:mb-10">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
              <i className="fas fa-user text-emerald-400 text-xl"></i>
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-neutral-900 dark:text-white">
                Welcome back, {user?.username}!
              </h1>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">{user?.email}</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-8">
          {statCards.map((stat, i) => (
            <div key={i} className="p-5 md:p-6 rounded-2xl bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800">
              <div className="flex items-center gap-3 mb-3">
                <i className={`fas ${stat.icon} text-2xl ${stat.color}`}></i>
                <span className="text-xs uppercase tracking-wider text-neutral-600 dark:text-neutral-400 font-semibold">
                  {stat.label}
                </span>
              </div>
              <div className="text-2xl md:text-3xl font-bold text-neutral-900 dark:text-white">
                {loading ? '—' : stat.value}
              </div>
            </div>
          ))}
        </div>

        <div className="mb-8">
          <h2 className="text-sm font-bold uppercase tracking-wider text-emerald-400 mb-4">
            <i className="fas fa-bolt mr-2"></i>Quick Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link to="/arena" className="group p-5 rounded-2xl bg-gradient-to-br from-emerald-900/50 to-neutral-900 border border-emerald-800/50 hover:border-emerald-500/50 transition-all">
              <i className="fas fa-play-circle text-3xl text-emerald-400 mb-3"></i>
              <h3 className="font-bold text-neutral-900 dark:text-white mb-1">Enter Arena</h3>
              <p className="text-xs text-neutral-600 dark:text-neutral-400">Start a new challenge</p>
            </Link>
            <Link to="/learning-paths" className="p-5 rounded-2xl bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800 hover:border-emerald-500/30 transition-all">
              <i className="fas fa-book text-3xl text-blue-400 mb-3"></i>
              <h3 className="font-bold text-neutral-900 dark:text-white mb-1">Browse Paths</h3>
              <p className="text-xs text-neutral-600 dark:text-neutral-400">Explore all learning paths</p>
            </Link>
            <Link to="/leaderboard" className="p-5 rounded-2xl bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800 hover:border-emerald-500/30 transition-all">
              <i className="fas fa-trophy text-3xl text-yellow-400 mb-3"></i>
              <h3 className="font-bold text-neutral-900 dark:text-white mb-1">Leaderboard</h3>
              <p className="text-xs text-neutral-600 dark:text-neutral-400">See where you rank</p>
            </Link>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800">
          <h2 className="text-sm font-bold uppercase tracking-wider text-emerald-400 mb-4">
            <i className="fas fa-clock-rotate-left mr-2"></i>Recent Activity
          </h2>
          {loading ? (
            <div className="text-center py-8 text-neutral-500 text-sm">Loading...</div>
          ) : !stats?.recent_activity?.length ? (
            <div className="text-center py-8 text-neutral-500">
              <i className="fas fa-inbox text-4xl mb-3 opacity-50"></i>
              <p className="text-sm">No recent activity yet.</p>
              <p className="text-xs mt-1">Start a challenge to begin your journey!</p>
            </div>
          ) : (
            <ul className="divide-y divide-neutral-200 dark:divide-neutral-800">
              {stats.recent_activity.map((item, i) => (
                <li key={i} className="py-3 flex items-center gap-3">
                  <i className={`fas ${item.type === 'lesson' ? 'fa-book-open text-blue-400' : 'fa-flag text-emerald-400'}`}></i>
                  <span className="text-sm text-neutral-900 dark:text-white flex-1">{item.title}</span>
                  <span className="text-xs text-neutral-500">
                    {new Date(item.completed_at).toLocaleDateString()}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
