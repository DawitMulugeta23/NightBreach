import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authApi, tokenStorage } from '../utils/api'
import { useAuth } from '../context/AuthContext'

function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    institution: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleChange = (e) => setFormData({ ...formData, [e.target.id]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (formData.password !== formData.confirmPassword) return setError('Passwords do not match')
    if (formData.password.length < 8) return setError('Password must be at least 8 characters')

    setLoading(true)
    try {
      const data = await authApi.register(formData.username, formData.email, formData.password)
      tokenStorage.set(data.access_token)
      const userData = await authApi.getCurrentUser(data.access_token)
      login(data.access_token, userData)
      navigate('/')
    } catch (err) {
      setError(err.message)
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
          REGISTER
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4 bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-6 md:p-8 backdrop-blur-sm shadow-2xl shadow-black/50">
          <div className="input-group">
            <i className="fas fa-user text-neutral-500"></i>
            <input id="username" type="text" placeholder="Username" value={formData.username} onChange={handleChange} className="input-field" required disabled={loading} />
          </div>
          <div className="input-group">
            <i className="fas fa-envelope text-neutral-500"></i>
            <input id="email" type="email" placeholder="Email Address" value={formData.email} onChange={handleChange} className="input-field" required disabled={loading} />
          </div>
          <div className="input-group">
            <i className="fas fa-lock text-neutral-500"></i>
            <input id="password" type="password" placeholder="Password" value={formData.password} onChange={handleChange} className="input-field" required disabled={loading} />
          </div>
          <div className="input-group">
            <i className="fas fa-lock text-neutral-500"></i>
            <input id="confirmPassword" type="password" placeholder="Confirm Password" value={formData.confirmPassword} onChange={handleChange} className="input-field" required disabled={loading} />
          </div>
          <div className="input-group">
            <i className="fas fa-building text-neutral-500"></i>
            <input id="institution" type="text" placeholder="Ethiopian Institution/Affiliation" value={formData.institution} onChange={handleChange} className="input-field" disabled={loading} />
          </div>

          <label className="flex items-start gap-2 text-xs text-neutral-600 dark:text-neutral-400 pt-1 cursor-pointer">
            <input type="checkbox" required className="accent-emerald-500 mt-0.5" />
            <span>
              Agree to <a href="#" className="text-emerald-400">Terms of Service</a>
            </span>
          </label>

          <button type="submit" disabled={loading} className="btn-primary w-full py-3 text-sm flex items-center justify-center gap-2 disabled:opacity-50">
            {loading ? (
              <>
                <i className="fas fa-spinner fa-spin"></i> REGISTERING...
              </>
            ) : (
              <>
                <i className="fas fa-user-plus"></i> REGISTER
              </>
            )}
          </button>
        </form>

        <div className="text-center text-xs text-neutral-600 dark:text-neutral-400 mt-6 space-y-2">
          <div>
            Already have an account?{' '}
            <Link to="/login" className="text-emerald-400 hover:text-emerald-300 transition-colors">
              <i className="fas fa-sign-in-alt mr-1"></i>Login
            </Link>
          </div>
          <div>
            <Link to="/" className="hover:text-neutral-200 transition-colors">
              <i className="fas fa-arrow-left mr-1"></i>Back to Network Map
            </Link>
          </div>
        </div>

        <p className="text-center text-[11px] text-neutral-600 dark:text-neutral-400 mt-8">
          <i className="fas fa-shield-check text-emerald-400 mr-1"></i>
          Secure Infrastructure & Monitoring<br />&copy; 2025 NightBreach
        </p>
      </div>
    </div>
  )
}

export default Register
