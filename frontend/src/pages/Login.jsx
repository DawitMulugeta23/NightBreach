import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { authApi, tokenStorage } from '../utils/api'
import { useAuth } from '../context/AuthContext'

function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    const toastId = toast.loading('Signing you in...')
    try {
      const data = await authApi.login(username, password)
      tokenStorage.set(data.access_token)
      const userData = await authApi.getCurrentUser(data.access_token)
      login(data.access_token, userData)
      toast.success(`Welcome back, ${userData.username}!`, { id: toastId })
      navigate('/')
    } catch (err) {
      setError(err.message)
      toast.error(err.message || 'Login failed', { id: toastId })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-200px)] flex items-center justify-center px-4 py-14 relative overflow-hidden">
      <div className="absolute inset-0 z-0">
        <img src="/ethioctf.jpeg" alt="" className="w-full h-full object-cover opacity-30" />
        <div className="absolute inset-0 bg-gradient-to-b from-neutral-950/70 via-neutral-950/50 to-neutral-950/70"></div>
      </div>

      <div className="relative z-10 w-full max-w-md">
        <div className="relative mx-auto mb-6 w-20 h-20 md:w-24 md:h-24 flex items-center justify-center">
          <div className="absolute inset-0 rounded-full bg-emerald-500/30 blur-2xl"></div>
          <i className="fas fa-shield-halved text-4xl md:text-5xl text-emerald-400 relative drop-shadow-[0_0_20px_rgba(52,211,153,0.5)]"></i>
        </div>

        <h1 className="text-center text-sm md:text-base font-bold uppercase tracking-wide mb-6 text-neutral-900 dark:text-white flex items-center justify-center gap-2">
          <i className="fas fa-map-pin text-emerald-400"></i>
          NightBreach: ETHIOPIAN CYBER DEFENSE NETWORK
        </h1>

        {error && (
          <div className="text-center text-red-400 text-xs mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
            <i className="fas fa-circle-exclamation mr-2"></i>
            {error}
          </div>
        )}

        <h2 className="text-center text-emerald-400 font-bold uppercase tracking-widest text-2xl md:text-3xl mb-8">
          LOGIN
        </h2>

        <form onSubmit={handleSubmit} className="space-y-5 bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-6 md:p-8 backdrop-blur-sm shadow-2xl shadow-black/50">
          <div className="input-group">
            <i className="fas fa-user text-neutral-500"></i>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="input-field"
              required
              disabled={loading}
            />
          </div>

          <div className="input-group">
            <i className="fas fa-lock text-neutral-500"></i>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field"
              required
              disabled={loading}
            />
          </div>

          <div className="flex items-center justify-between text-xs text-neutral-600 dark:text-neutral-400">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" className="accent-emerald-500" />
              Remember me
            </label>
            <a href="#" className="hover:text-emerald-400 transition-colors">
              <i className="fas fa-key mr-1"></i>
              Forgot Password?
            </a>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full py-3 text-sm flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <i className="fas fa-spinner fa-spin"></i>
                LOGGING IN...
              </>
            ) : (
              <>
                <i className="fas fa-sign-in-alt"></i>
                LOGIN
              </>
            )}
          </button>
        </form>

        <div className="text-center text-xs text-neutral-600 dark:text-neutral-400 mt-6 space-y-2">
          <div>
            <Link to="/register" className="text-emerald-400 hover:text-emerald-300 transition-colors">
              <i className="fas fa-user-plus mr-1"></i>
              Create an account
            </Link>
          </div>
          <div>
            <Link to="/" className="hover:text-neutral-200 transition-colors">
              <i className="fas fa-arrow-left mr-1"></i>
              Back to Network Map
            </Link>
          </div>
        </div>

        <p className="text-center text-[11px] text-neutral-600 dark:text-neutral-400 mt-8">
          <i className="fas fa-shield-check text-emerald-400 mr-1"></i>
          Secure Infrastructure & Monitoring<br />
          &copy; 2025 NightBreach
        </p>
      </div>
    </div>
  )
}

export default Login
