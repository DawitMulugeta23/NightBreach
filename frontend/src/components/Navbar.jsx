import React, { useState, useRef, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { NAV_LINKS } from '../utils/constants'

function Navbar() {
  const location = useLocation()
  const navigate = useNavigate()
  const path = location.pathname
  const { user, logout, isAuthenticated } = useAuth()
  const { isDark, toggleTheme } = useTheme()
  const visibleLinks = isAuthenticated ? NAV_LINKS : []
  const [mobileOpen, setMobileOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const profileRef = useRef(null)

  const handleLogout = () => {
    setProfileOpen(false)
    logout()
    toast.success('Logged out')
    navigate('/')
  }

  useEffect(() => {
    const onClickOutside = (e) => {
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setProfileOpen(false)
      }
    }
    document.addEventListener('mousedown', onClickOutside)
    return () => document.removeEventListener('mousedown', onClickOutside)
  }, [])

  useEffect(() => {
    setProfileOpen(false)
    setMobileOpen(false)
  }, [path])

  return (
    <nav className="sticky top-0 z-50 border-b border-neutral-200 dark:border-neutral-800 bg-white/95 dark:bg-neutral-950/95 backdrop-blur-sm">
      <div className="flex items-center justify-between px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-4">
        <Link to="/" className="flex items-center gap-2 md:gap-3">
          <i className="fas fa-shield-halved text-emerald-400 text-xl md:text-2xl"></i>
          <span className="text-base md:text-lg font-bold tracking-wide text-neutral-900 dark:text-white">NightBreach</span>
        </Link>

        <div className="hidden md:flex items-center gap-6 lg:gap-8 text-xs font-semibold uppercase tracking-wider">
          {visibleLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={`transition-colors ${
                path === link.to ? 'text-emerald-400' : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-200'
              }`}
            >
              {link.label}
            </Link>
          ))}
          {isAuthenticated && (
            <Link
              to="/dashboard"
              className={`transition-colors ${
                path === '/dashboard' ? 'text-emerald-400' : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-200'
              }`}
            >
              Dashboard
            </Link>
          )}
        </div>

        <div className="flex items-center gap-2 md:gap-4">
          <button
            onClick={toggleTheme}
            className="w-9 h-9 flex items-center justify-center rounded bg-neutral-100 dark:bg-neutral-800 hover:bg-neutral-200 dark:hover:bg-neutral-700 border border-neutral-300 dark:border-neutral-700 cursor-pointer transition-colors"
            aria-label="Toggle theme"
          >
            <i className={`fas ${isDark ? 'fa-sun text-yellow-400' : 'fa-moon text-neutral-600'}`}></i>
          </button>
          {isAuthenticated ? (
            <div className="relative" ref={profileRef}>
              <button
                onClick={() => setProfileOpen((o) => !o)}
                className="flex items-center gap-2 md:gap-3 px-2 py-1.5 rounded-lg bg-neutral-100 dark:bg-neutral-800 hover:bg-neutral-200 dark:hover:bg-neutral-700 border border-neutral-300 dark:border-neutral-700 cursor-pointer transition-colors"
                aria-label="Profile menu"
                aria-expanded={profileOpen}
              >
                <i className="fas fa-user-circle text-emerald-400 text-3xl md:text-4xl"></i>
                <span className="hidden sm:inline text-xs font-semibold text-neutral-900 dark:text-white">
                  {user?.username}
                </span>
                <i className={`fas fa-chevron-down text-[10px] text-neutral-600 dark:text-neutral-400 transition-transform ${profileOpen ? 'rotate-180' : ''}`}></i>
              </button>

              {profileOpen && (
                <div className="absolute right-0 mt-2 w-48 rounded-lg bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 shadow-xl shadow-black/20 dark:shadow-black/50 overflow-hidden z-50">
                  <div className="px-4 py-3 border-b border-neutral-200 dark:border-neutral-800">
                    <p className="text-[10px] uppercase tracking-wider text-neutral-500 dark:text-neutral-500">
                      Signed in as
                    </p>
                    <p className="text-sm font-semibold text-neutral-900 dark:text-white truncate">
                      {user?.username}
                    </p>
                  </div>

                  <Link
                    to="/dashboard"
                    onClick={() => setProfileOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-xs font-semibold text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
                  >
                    <i className="fas fa-gauge-high text-emerald-400 w-4"></i>
                    Dashboard
                  </Link>

                  <Link
                    to="/settings"
                    onClick={() => setProfileOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-xs font-semibold text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
                  >
                    <i className="fas fa-gear text-emerald-400 w-4"></i>
                    Settings
                  </Link>

                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-4 py-2.5 text-xs font-semibold text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors border-t border-neutral-200 dark:border-neutral-800 cursor-pointer"
                  >
                    <i className="fas fa-sign-out-alt w-4"></i>
                    Logout
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link
              to="/login"
              className="px-4 py-2 text-xs font-semibold uppercase tracking-wide rounded bg-neutral-100 dark:bg-neutral-800 hover:bg-neutral-200 dark:hover:bg-neutral-700 border border-neutral-300 dark:border-neutral-700 cursor-pointer transition-colors text-neutral-900 dark:text-white flex items-center gap-2"
            >
              <i className="fas fa-sign-in-alt text-emerald-400"></i>
              Login / Join
            </Link>
          )}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden text-neutral-900 dark:text-white"
          >
            <i className={`fas ${mobileOpen ? 'fa-times' : 'fa-bars'} text-xl`}></i>
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden px-4 pb-4 border-t border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-950">
          {visibleLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              onClick={() => setMobileOpen(false)}
              className={`block py-3 text-sm font-semibold uppercase tracking-wider border-b border-neutral-200 dark:border-neutral-800 ${
                path === link.to ? 'text-emerald-400' : 'text-neutral-600 dark:text-neutral-400'
              }`}
            >
              {link.label}
            </Link>
          ))}
          {isAuthenticated && (
            <Link
              to="/dashboard"
              onClick={() => setMobileOpen(false)}
              className="block py-3 text-sm font-semibold uppercase tracking-wider text-neutral-600 dark:text-neutral-400"
            >
              Dashboard
            </Link>
          )}
        </div>
      )}
    </nav>
  )
}

export default Navbar
