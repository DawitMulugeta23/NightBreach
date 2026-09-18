import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { learningApi, tokenStorage } from '../utils/api'
import { useAuth } from '../context/AuthContext'
import MapBackground from '../components/MapBackground'
import LoadingSpinner from '../components/LoadingSpinner'

function LearningPaths() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [paths, setPaths] = useState([])
  const [loading, setLoading] = useState(false)
  const [clicking, setClicking] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!isAuthenticated) return
    const token = tokenStorage.get()
    if (!token) return
    setLoading(true)
    learningApi
      .listPaths(token)
      .then(setPaths)
      .catch((err) => {
        setError(err.message)
        toast.error(err.message || 'Failed to load learning paths')
      })
      .finally(() => setLoading(false))
  }, [isAuthenticated])

  const iconBySlug = {
    'linux-fundamentals': '/linuxlogo.jpeg',
    'web-application-hacking': '/webapppentest.jpg',
    'web-app-hacking': '/webapppentest.jpg',
    'cyber-security': '/fundamentalCybersecurity.jpeg',
    'fundamental-cybersecurity': '/fundamentalCybersecurity.jpeg',
    'defensive-security': '/defensive.jpeg',
    'defensive': '/defensive.jpeg',
    'offensive-security': '/offensive.jpeg',
    'offensive': '/offensive.jpeg',
    'networking-fundamentals': '/Networking.jpg',
    'networking': '/Networking.jpg',
  }

  const defaultIconByIndex = [
    '/linuxlogo.jpeg',
    '/Networking.jpg',
    '/fundamentalCybersecurity.jpeg',
    '/defensive.jpeg',
    '/offensive.jpeg',
    '/webapppentest.jpg',
  ]

  const staticPaths = [
    { id: 'static-linux',      slug: 'linux-fundamentals',        title: 'Linux Fundamentals',       description: 'Master CLI navigation, file permissions, user management, and process control.' },
    { id: 'static-networking', slug: 'networking-fundamentals',   title: 'Networking Fundamentals',  description: 'Understand TCP/IP, subnetting, VLANs, routing, and essential protocols.' },
    { id: 'static-cyber',      slug: 'fundamental-cybersecurity', title: 'Cyber Security',           description: 'Core principles of information security, risk management, and threat landscapes.' },
    { id: 'static-defensive',  slug: 'defensive-security',        title: 'Defensive Security',       description: 'Learn to detect, prevent, and mitigate attacks and harden systems.' },
    { id: 'static-offensive',  slug: 'offensive-security',        title: 'Offensive Security',       description: 'Understand ethical hacking techniques, vulnerability exploitation, and post-exploitation.' },
    { id: 'static-webapp',     slug: 'web-app-hacking',           title: 'Web Application Hacking',  description: 'Analyze and exploit OWASP Top 10 web vulnerabilities and tackle complex labs.' },
  ]

  const displayPaths = paths.length > 0 ? paths : staticPaths

  const getIcon = (path, index) => {
    if (iconBySlug[path.slug]) return iconBySlug[path.slug]
    return defaultIconByIndex[index % defaultIconByIndex.length]
  }

  const handlePathClick = async (path) => {
    if (!isAuthenticated) {
      toast('Please log in to start learning', { icon: '🔒' })
      return navigate('/login')
    }

    if (path.id.startsWith('static-')) {
      toast('This path is coming soon!', { icon: '🚧' })
      return
    }

    setClicking(path.id)
    try {
      const token = tokenStorage.get()
      const detail = await learningApi.getPath(path.id, token)
      if (!detail.rooms?.length) {
        toast('No rooms in this path yet. Content coming soon!', { icon: '🚧' })
        return
      }
      navigate(`/learning/paths/${path.id}`)
    } catch (err) {
      toast.error('Failed to load path: ' + err.message)
    } finally {
      setClicking(null)
    }
  }


  return (
    <div className="relative w-full min-h-screen px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-8 md:py-12 overflow-hidden bg-white dark:bg-neutral-950">
      <MapBackground position="top-right" opacity={20} />

      <div className="relative max-w-7xl mx-auto">
        <div className="mb-10">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
              <i className="fas fa-graduation-cap text-emerald-400 text-xl"></i>
            </div>
            <h1 className="text-2xl md:text-3xl lg:text-4xl font-bold text-neutral-900 dark:text-white">
              Learning Paths
            </h1>
          </div>
          <p className="text-neutral-600 dark:text-neutral-400 text-sm md:text-base ml-14">
            Structured, gradual progress curriculum for ethical hacking mastery
          </p>
        </div>

        {loading && <LoadingSpinner message="Loading paths..." />}

        {!loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 md:gap-6">
            {displayPaths.map((p, i) => (
              <button
                key={p.id}
                onClick={() => handlePathClick(p)}
                disabled={clicking === p.id}
                className="group relative bg-gradient-to-br from-neutral-900 to-neutral-950 rounded-2xl border border-neutral-200 dark:border-neutral-800 hover:border-emerald-500/40 transition-all duration-500 overflow-hidden hover:shadow-2xl hover:shadow-emerald-500/10 hover:-translate-y-2 text-left disabled:opacity-50"
              >
                <div className="relative p-5 md:p-6 flex flex-col items-center text-center">
                  <div className="relative mb-4">
                    <div className="w-24 h-24 md:w-28 md:h-28 rounded-full overflow-hidden border-2 border-neutral-300 dark:border-neutral-700 group-hover:border-emerald-400/60 transition-all duration-300 shadow-lg shadow-black/30 group-hover:shadow-emerald-500/20">
                      <img
                        src={getIcon(p, i)}
                        alt={p.title}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                      />
                    </div>
                    <div className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
                      <i className="fas fa-check text-emerald-400 text-[10px]"></i>
                    </div>
                  </div>

                  <h3 className="font-bold text-neutral-900 dark:text-white text-sm md:text-base mb-2 leading-tight">
                    {p.title}
                  </h3>

                  <p className="text-xs text-neutral-600 dark:text-neutral-400 leading-relaxed mb-4 line-clamp-2">
                    {p.description}
                  </p>

                  <div className="flex items-center gap-2 text-xs text-emerald-400 font-semibold">
                    {clicking === p.id ? (
                      <>
                        <i className="fas fa-spinner fa-spin"></i> Loading...
                      </>
                    ) : (
                      <>
                        {isAuthenticated ? 'Explore Path' : 'Login to Start'}
                        <i className="fas fa-arrow-right text-[10px] group-hover:translate-x-1 transition-transform"></i>
                      </>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>


    </div>
  )
}

export default LearningPaths
