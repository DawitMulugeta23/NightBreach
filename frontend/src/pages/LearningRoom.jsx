import React, { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { learningApi, tokenStorage } from '../utils/api'
import { useAuth } from '../context/AuthContext'
import MapBackground from '../components/MapBackground'
import Breadcrumb from '../components/Breadcrumb'
import LoadingSpinner from '../components/LoadingSpinner'

function LearningRoom() {
  const { pathId, roomId } = useParams()
  const navigate = useNavigate()
  const { isAuthenticated, loading: authLoading } = useAuth()

  const [path, setPath] = useState(null)
  const [room, setRoom] = useState(null)
  const [lessons, setLessons] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated) return navigate('/login')
    if (!pathId || !roomId) {
      setError('Invalid path or room')
      setLoading(false)
      return
    }

    const token = tokenStorage.get()
    if (!token) return

    async function load() {
      try {
        const [pathData, lessonsData] = await Promise.all([
          learningApi.getPath(pathId, token),
          learningApi.listRoomLessons(roomId, token),
        ])
        setPath(pathData)
        const roomData = pathData.rooms?.find((r) => r.id === roomId)
        if (!roomData) {
          setError('Room not found in this path')
          return
        }
        setRoom(roomData)
        setLessons(lessonsData)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [pathId, roomId, isAuthenticated, authLoading, navigate])

  if (authLoading || loading) return <LoadingSpinner message="Loading room..." />

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

  return (
    <div className="relative w-full min-h-screen px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-8 md:py-12 overflow-hidden bg-white dark:bg-neutral-950">
      <MapBackground position="top-right" opacity={20} />

      <div className="relative max-w-5xl mx-auto">
        <Breadcrumb
          items={[
            { label: 'Learning Paths', to: '/learning-paths' },
            { label: path?.title, to: `/learning/paths/${path?.id}/rooms/${roomId}` },
            { label: room?.title },
          ]}
        />

        <div className="mb-8">
          <h1 className="text-2xl md:text-3xl font-bold text-neutral-900 dark:text-white mb-2 flex items-center gap-3">
            <i className="fas fa-door-open text-emerald-400"></i>
            {room?.title}
          </h1>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 ml-11">{room?.description}</p>
        </div>

        {lessons.length === 0 ? (
          <div className="p-8 rounded-2xl bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800 text-center text-neutral-600 dark:text-neutral-400">
            <i className="fas fa-inbox text-4xl mb-3 opacity-50"></i>
            <p>No lessons in this room yet.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {lessons.map((lesson, i) => (
              <Link
                key={lesson.id}
                to={`/learning/lessons/${lesson.id}`}
                className={`group flex items-center justify-between p-5 rounded-2xl border transition-all duration-300 hover:shadow-lg ${
                  lesson.completed
                    ? 'bg-emerald-950/20 border-emerald-500/60 hover:border-emerald-400 hover:shadow-emerald-500/10'
                    : 'bg-neutral-50 dark:bg-neutral-900/80 border-neutral-200 dark:border-neutral-800 hover:border-emerald-500/50 hover:shadow-emerald-500/5'
                }`}
              >
                <div className="flex items-center gap-4">
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold ${
                      lesson.completed
                        ? 'bg-emerald-500 text-neutral-900 dark:text-white'
                        : 'bg-emerald-500/20 text-emerald-400'
                    }`}
                  >
                    {lesson.completed ? <i className="fas fa-check"></i> : i + 1}
                  </div>
                  <div>
                    <h3 className={`font-bold text-sm md:text-base ${lesson.completed ? 'text-emerald-300' : 'text-neutral-900 dark:text-white'}`}>
                      {lesson.title}
                    </h3>
                    <p className="text-xs text-neutral-500">
                      Lesson {lesson.order_index}
                      {lesson.completed && (
                        <span className="ml-3 text-emerald-400">
                          <i className="fas fa-check-circle mr-1"></i>
                          Completed
                        </span>
                      )}
                    </p>
                  </div>
                </div>
                {lesson.completed ? (
                  <i className="fas fa-square-check text-emerald-400 text-xl"></i>
                ) : (
                  <i className="fas fa-arrow-right text-neutral-500 group-hover:text-emerald-400 group-hover:translate-x-1 transition-all"></i>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default LearningRoom
