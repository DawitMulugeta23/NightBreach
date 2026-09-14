import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import MapBackground from '../components/MapBackground'
import { useAuth } from '../context/AuthContext'

function Challenges() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const tiers = [
    { tier: 'TIER 1', title: 'Entry Level Practice', levels: 'Approx. 50 levels', available: true, btnText: 'Enter Arena', icon: 'fa-flag', to: '/arena' },
    { tier: 'TIER 2', title: 'Intermediate Challenges', levels: 'Approx. 50 levels', available: false, btnText: 'Coming Soon', icon: 'fa-star' },
    { tier: 'TIER 3', title: 'Advanced Pen-Test', levels: 'Approx. 50 levels', available: false, btnText: 'Coming Soon', icon: 'fa-trophy' },
  ]

  const handleClick = (tier) => {
    if (!isAuthenticated) {
      toast('Please log in to enter the arena', { icon: '🔒' })
      navigate('/login')
      return
    }
    navigate(tier.to)
  }

  return (
    <div className="relative w-full min-h-screen px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-8 md:py-12 overflow-hidden bg-white dark:bg-neutral-950">
      <MapBackground position="top-right" opacity={20} />

      <div className="relative max-w-7xl mx-auto">
        <h1 className="text-xl md:text-2xl lg:text-3xl font-bold text-neutral-900 dark:text-white mb-2">
          <i className="fas fa-code text-emerald-400 mr-3"></i>CHALLENGES
        </h1>
        <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-8 md:mb-10">
          <i className="fas fa-bolt text-emerald-400 mr-2"></i>
          Test your skills with hands-on cybersecurity challenges.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
          {tiers.map((t, i) => (
            <div
              key={i}
              className={`p-6 md:p-8 rounded-2xl bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800 ${
                t.available
                  ? 'hover:border-emerald-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-emerald-500/5 hover:-translate-y-1'
                  : 'opacity-60'
              }`}
            >
              <div
                className={`text-xs font-bold mb-2 flex items-center gap-2 ${
                  t.available ? 'text-emerald-400' : 'text-neutral-500'
                }`}
              >
                <i className={`fas ${t.icon}`}></i>
                {t.tier}
              </div>
              <h3 className="text-lg font-bold text-neutral-900 dark:text-white mb-2">{t.title}</h3>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-6">{t.levels}</p>
              {t.available ? (
                <button
                  onClick={() => handleClick(t)}
                  className="btn-primary w-full block text-center flex items-center justify-center gap-2"
                >
                  <i className="fas fa-arrow-right"></i>
                  {t.btnText}
                </button>
              ) : (
                <button
                  disabled
                  className="w-full px-4 py-2.5 text-sm font-semibold rounded-xl bg-neutral-100 dark:bg-neutral-800 text-neutral-500 cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <i className="fas fa-lock"></i>
                  {t.btnText}
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Challenges
