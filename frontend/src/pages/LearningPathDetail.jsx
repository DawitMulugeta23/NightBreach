import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { learningApi, tokenStorage } from '../utils/api'
import { useAuth } from '../context/AuthContext'
import MapBackground from '../components/MapBackground'
import LoadingSpinner from '../components/LoadingSpinner'
import Breadcrumb from '../components/Breadcrumb'

const ROOM_THEMES = {
  1: { label: 'Fundamental', color: 'emerald', icon: 'fa-seedling' },
  2: { label: 'Intermediate', color: 'sky',    icon: 'fa-code-branch' },
  3: { label: 'Advanced',     color: 'amber',  icon: 'fa-bolt' },
  4: { label: 'Master',       color: 'rose',   icon: 'fa-crown' },
}

const COLOR_CLASSES = {
  emerald: {
    dot:      'bg-emerald-400 border-emerald-400',
    dotEmpty: 'bg-neutral-200 dark:bg-neutral-800 border-emerald-400/60',
    line:     'bg-emerald-500/50',
    icon:     'text-emerald-400',
    ring:     'bg-emerald-500/20',
    badge:    'text-emerald-400 bg-emerald-500/10 border-emerald-500/40',
  },
  sky: {
    dot:      'bg-sky-400 border-sky-400',
    dotEmpty: 'bg-neutral-200 dark:bg-neutral-800 border-sky-400/60',
    line:     'bg-sky-500/50',
    icon:     'text-sky-400',
    ring:     'bg-sky-500/20',
    badge:    'text-sky-400 bg-sky-500/10 border-sky-500/40',
  },
  amber: {
    dot:      'bg-amber-400 border-amber-400',
    dotEmpty: 'bg-neutral-200 dark:bg-neutral-800 border-amber-400/60',
    line:     'bg-amber-500/50',
    icon:     'text-amber-400',
    ring:     'bg-amber-500/20',
    badge:    'text-amber-400 bg-amber-500/10 border-amber-500/40',
  },
  rose: {
    dot:      'bg-rose-400 border-rose-400',
    dotEmpty: 'bg-neutral-200 dark:bg-neutral-800 border-rose-400/60',
    line:     'bg-rose-500/50',
    icon:     'text-rose-400',
    ring:     'bg-rose-500/20',
    badge:    'text-rose-400 bg-rose-500/10 border-rose-500/40',
  },
}

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

  const handleRoomClick = (room) => {
    if (!room.lesson_count || room.lesson_count === 0) {
      toast('This room is coming soon!', { icon: '🚧' })
      return
    }
    navigate(`/learning/paths/${path.id}/rooms/${room.id}`)
  }

  return (
    <div className="relative w-full min-h-screen px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-8 md:py-12 overflow-hidden bg-white dark:bg-neutral-950">
      <MapBackground position="top-right" opacity={20} />

      <div className="relative max-w-3xl mx-auto">
        <Breadcrumb
          items={[
            { label: 'Learning Paths', to: '/learning-paths' },
            { label: path.title },
          ]}
        />

        {/* Header */}
        <div className="mb-10">
          <div className="flex items-center gap-4 mb-3">
            {path.icon && (
              <div className="w-16 h-16 rounded-2xl overflow-hidden border-2 border-neutral-200 dark:border-neutral-800 flex-shrink-0">
                <img src={path.icon} alt={path.title} className="w-full h-full object-cover" />
              </div>
            )}
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-neutral-900 dark:text-white">
                {path.title}
              </h1>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
                {path.description}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4 mt-4 text-xs text-neutral-500">
            <span className="flex items-center gap-1.5">
              <i className="fas fa-door-open text-emerald-400"></i>
              {rooms.length} rooms
            </span>
            <span className="flex items-center gap-1.5">
              <i className="fas fa-book text-emerald-400"></i>
              {rooms.reduce((sum, r) => sum + (r.lesson_count || 0), 0)} lessons
            </span>
          </div>
        </div>

        {/* Roadmap */}
        <div className="relative">
          {rooms.length === 0 && (
            <div className="p-8 rounded-2xl bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800 text-center text-neutral-600 dark:text-neutral-400">
              <i className="fas fa-inbox text-4xl mb-3 opacity-50"></i>
              <p>No rooms in this path yet.</p>
            </div>
          )}

          {rooms.map((room, i) => {
            const theme = ROOM_THEMES[room.order_index] || ROOM_THEMES[1]
            const colors = COLOR_CLASSES[theme.color] || COLOR_CLASSES.emerald
            const hasLessons = room.lesson_count > 0
            const isLast = i === rooms.length - 1

            return (
              <div key={room.id} className="relative flex items-stretch gap-5">
                {/* Vertical roadmap column: dot + connector line */}
                <div className="flex flex-col items-center flex-shrink-0" style={{ width: '2rem' }}>
                  <div
                    className={`w-4 h-4 rounded-full border-2 mt-6 transition-all ${
                      hasLessons ? colors.dot : colors.dotEmpty
                    } ${hasLessons ? 'shadow-lg shadow-black/20' : ''}`}
                  />
                  {!isLast && (
                    <div className={`w-0.5 flex-1 my-1 ${colors.line}`} />
                  )}
                </div>

                {/* Room card */}
                <button
                  onClick={() => handleRoomClick(room)}
                  disabled={!hasLessons}
                  className={`group flex-1 my-3 text-left p-5 md:p-6 rounded-2xl border transition-all duration-300 ${
                    hasLessons
                      ? 'bg-neutral-50 dark:bg-neutral-900/80 border-neutral-200 dark:border-neutral-800 hover:border-emerald-500/60 hover:shadow-xl hover:shadow-emerald-500/5 hover:-translate-y-0.5 cursor-pointer'
                      : 'bg-neutral-50/60 dark:bg-neutral-900/50 border-neutral-200 dark:border-neutral-800 opacity-60 cursor-not-allowed'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-4 min-w-0">
                      <div
                        className={`w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 ${colors.ring}`}
                      >
                        <i className={`fas ${theme.icon} ${colors.icon} text-lg`}></i>
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <span
                            className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${colors.badge}`}
                          >
                            Room {room.order_index} · {theme.label}
                          </span>
                          {hasLessons ? (
                            <span className="text-[10px] text-neutral-500">
                              {room.lesson_count} {room.lesson_count === 1 ? 'lesson' : 'lessons'}
                            </span>
                          ) : (
                            <span className="text-[10px] text-neutral-500 uppercase tracking-wider">
                              Coming soon
                            </span>
                          )}
                        </div>
                        <h3 className="text-base md:text-lg font-bold text-neutral-900 dark:text-white mb-1">
                          {room.title}
                        </h3>
                        <p className="text-xs md:text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed">
                          {room.description}
                        </p>
                      </div>
                    </div>
                    {hasLessons && (
                      <i className="fas fa-arrow-right text-neutral-400 group-hover:text-emerald-400 group-hover:translate-x-1 transition-all self-center flex-shrink-0"></i>
                    )}
                  </div>
                </button>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default LearningPathDetail
