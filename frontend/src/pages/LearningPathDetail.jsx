import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { learningApi, tokenStorage } from '../utils/api'
import { useAuth } from '../context/AuthContext'
import MapBackground from '../components/MapBackground'
import LoadingSpinner from '../components/LoadingSpinner'
import Breadcrumb from '../components/Breadcrumb'

const DISPLAY_TEXT = {
  'offensive-security': {
    title: 'Offensive Cybersecurity Pathway',
    subtitle: 'From Beginner to Red Teamer: A Zero-to-Hero Journey',
    cta: 'Start your Red Team career today.',
  },
}

function pickIcon(title = '') {
  const t = title.toLowerCase()
  if (t.includes('cybersecurity zero') || t.includes('essential')) return 'fa-lock'
  if (t.includes('linux')) return 'fa-terminal'
  if (t.includes('network')) return 'fa-globe'
  if (t.includes('recon') || t.includes('osint')) return 'fa-magnifying-glass'
  if (t.includes('vulnerab')) return 'fa-book'
  if (t.includes('exploit')) return 'fa-terminal'
  if (t.includes('web')) return 'fa-code'
  if (t.includes('privilege') || t.includes('privesc')) return 'fa-hashtag'
  if (t.includes('red team')) return 'fa-shield-cat'
  return 'fa-book'
}

const ICON_BG = [
  'bg-gradient-to-br from-violet-600 to-purple-800',
  'bg-gradient-to-br from-blue-600 to-blue-800',
  'bg-gradient-to-br from-cyan-500 to-cyan-700',
  'bg-gradient-to-br from-rose-600 to-pink-800',
  'bg-gradient-to-br from-orange-500 to-red-700',
  'bg-gradient-to-br from-neutral-700 to-neutral-900',
  'bg-gradient-to-br from-indigo-600 to-violet-800',
  'bg-gradient-to-br from-red-700 to-neutral-900',
  'bg-gradient-to-br from-red-800 to-neutral-950',
]

function LearningPathDetail() {
  const { pathId } = useParams()
  const navigate = useNavigate()
  const { isAuthenticated, loading: authLoading } = useAuth()

  const [path, setPath] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated) return navigate('/login')
    if (!pathId) {
      setError('No path selected')
      setLoading(false)
      return
    }

    const token = tokenStorage.get()
    if (!token) return

    learningApi
      .getPath(pathId, token)
      .then(setPath)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [pathId, isAuthenticated, authLoading, navigate])

  if (authLoading || loading) return <LoadingSpinner message="Loading path..." />

  if (error) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center px-4">
        <div className="text-center">
          <i className="fas fa-circle-exclamation text-4xl text-red-400 mb-4"></i>
          <p className="text-red-400 mb-4">{error}</p>
          <Link to="/learning-paths" className="btn-primary inline-block">
            Back to Learning Paths
          </Link>
        </div>
      </div>
    )
  }

  if (!path) return null

  const rooms = [...(path.rooms || [])].sort((a, b) => a.order_index - b.order_index)
  const firstUnlockedRoom = rooms.find((r) => r.lesson_count > 0 && !r.locked)
  const display = DISPLAY_TEXT[path.slug] || {
    title: path.title,
    subtitle: path.description,
    cta: 'Start your journey today.',
  }

  const handleRoomClick = (room) => {
    if (room.locked) {
      toast('Complete the previous module to unlock this one!', { icon: '🔒' })
      return
    }
    if (!room.lesson_count || room.lesson_count === 0) {
      toast('This module is coming soon!', { icon: '🚧' })
      return
    }
    navigate(`/learning/paths/${path.id}/rooms/${room.id}`)
  }

  const handleBeginPath = () => {
    if (firstUnlockedRoom) {
      handleRoomClick(firstUnlockedRoom)
    } else {
      toast('No modules available yet!', { icon: '🚧' })
    }
  }

  return (
    <div className="relative w-full min-h-screen px-4 sm:px-6 md:px-8 lg:px-12 py-8 md:py-12 overflow-hidden bg-neutral-950">
      <MapBackground position="top-right" opacity={12} />

      <div className="relative max-w-6xl mx-auto">
        <Breadcrumb
          items={[
            { label: 'Learning Paths', to: '/learning-paths' },
            { label: path.title },
          ]}
        />

        <div className="text-center mb-10">
          <h1 className="text-2xl md:text-4xl font-extrabold text-white tracking-tight uppercase">
            {display.title}
          </h1>
          <p className="text-neutral-400 text-sm md:text-base mt-2 max-w-2xl mx-auto">
            {display.subtitle}
          </p>
        </div>

        {rooms.length === 0 ? (
          <div className="p-8 rounded-2xl bg-neutral-900/80 border border-neutral-800 text-center text-neutral-400">
            <i className="fas fa-inbox text-4xl mb-3 opacity-50"></i>
            <p>No modules in this path yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 md:gap-6">
            {rooms.map((room, i) => {
              const hasLessons = room.lesson_count > 0
              const isLocked = !!room.locked
              const isClickable = hasLessons && !isLocked
              const col = i % 3
              const borderClass = col === 1
                ? 'border-fuchsia-500/70 hover:border-fuchsia-400'
                : 'border-cyan-400/70 hover:border-cyan-300'
              const linkClass = col === 1 ? 'text-fuchsia-400' : 'text-cyan-300'
              const iconBg = ICON_BG[i % ICON_BG.length]

              return (
                <button
                  key={room.id}
                  onClick={() => handleRoomClick(room)}
                  disabled={!isClickable}
                  className={`group text-left rounded-xl border-2 bg-neutral-900/90 p-5 transition-all duration-300 ${borderClass} ${
                    isClickable
                      ? 'hover:-translate-y-1 hover:shadow-xl hover:shadow-cyan-500/10 cursor-pointer'
                      : 'opacity-70 cursor-not-allowed'
                  }`}
                >
                  <div className="flex items-start gap-3 mb-2">
                    <div className={`w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0 shadow-lg ${iconBg}`}>
                      <i className={`fas ${isLocked ? 'fa-lock' : pickIcon(room.title)} text-white text-lg`}></i>
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="font-bold text-white text-sm md:text-base leading-tight">
                          {room.title}
                        </h3>
                        {i === 0 && (
                          <span className="text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                            Required
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <p className="text-xs text-neutral-400 leading-relaxed mb-3 line-clamp-2">
                    {room.description}
                  </p>
                  <span className={`text-xs font-semibold inline-flex items-center gap-1.5 ${isLocked ? 'text-neutral-500' : linkClass}`}>
                    {isLocked ? 'Complete previous module to unlock' : 'Explore Modules'}
                    {!isLocked && (
                      <i className="fas fa-arrow-right text-[10px] group-hover:translate-x-1 transition-transform"></i>
                    )}
                  </span>
                </button>
              )
            })}
          </div>
        )}

        {rooms.length > 0 && (
          <div className="mt-8 rounded-xl bg-neutral-900 border border-neutral-800 px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-white font-semibold text-sm md:text-base">
              {display.cta}
            </p>
            <button
              onClick={handleBeginPath}
              className="px-5 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-neutral-950 font-bold text-sm transition-colors"
            >
              Begin Path
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default LearningPathDetail
