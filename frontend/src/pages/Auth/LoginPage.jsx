import {
  AlertCircle,
  ArrowRight,
  Eye,
  EyeOff,
  Loader2,
  Lock,
  User,
} from 'lucide-react'
import {
  Link,
  useLocation,
  useNavigate,
} from 'react-router-dom'
import { useState } from 'react'

import NightBreachLogo from '../../components/common/NightBreachLogo.jsx'
import { useAuth } from '../../context/useAuth.js'
import nightbreachAssets from '../../config/nightbreachAssets.js'

function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()

  const { login } = useAuth()

  const [form, setForm] = useState({
    username: location.state?.username || '',
    password: '',
  })

  const [showPassword, setShowPassword] =
    useState(false)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const registered =
    location.state?.registered === true

  function updateField(event) {
    const { name, value } = event.target

    setForm((current) => ({
      ...current,
      [name]: value,
    }))
  }

  async function handleSubmit(event) {
    event.preventDefault()

    setError('')

    if (!form.username.trim() || !form.password) {
      setError(
        'Username and password are required.',
      )
      return
    }

    setLoading(true)

    try {
      await login({
        username: form.username.trim(),
        password: form.password,
      })

      const destination =
        location.state?.from || '/dashboard'

      navigate(destination, {
        replace: true,
      })
    } catch (requestError) {
      setError(
        requestError.message ||
          'Login failed. Please check your credentials.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#020711] text-slate-100">
      <div className="grid min-h-screen lg:grid-cols-[1.05fr_0.95fr]">

        <div className="relative hidden overflow-hidden border-r border-slate-800/70 lg:block">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_20%,rgba(0,126,255,.16),transparent_35%),radial-gradient(circle_at_75%_75%,rgba(139,92,246,.08),transparent_35%)]" />

          <img
            src={nightbreachAssets.illustrations.laptop3d}
            alt=""
            className="absolute bottom-8 right-4 w-[75%] max-w-[650px] opacity-40"
          />

          <div className="relative flex h-full flex-col justify-between p-10">
            <NightBreachLogo />

            <div className="max-w-lg">
              <div className="mb-4 text-xs font-semibold uppercase tracking-[0.18em] text-blue-400">
                Cybersecurity learning
              </div>

              <h1 className="text-4xl font-bold tracking-tight text-white">
                Welcome back to NightBreach.
              </h1>

              <p className="mt-5 max-w-md text-sm leading-7 text-slate-400">
                Continue your learning, practical
                exercises, CTF challenges, and skill
                development.
              </p>
            </div>

            <div className="text-xs text-slate-600">
              Learn → Practice → Challenge → Develop Skill
            </div>
          </div>
        </div>

        <div className="flex items-center justify-center px-5 py-10 sm:px-8">
          <div className="w-full max-w-md">

            <div className="mb-8 lg:hidden">
              <NightBreachLogo />
            </div>

            <div className="mb-8">
              <div className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-400">
                Authentication
              </div>

              <h2 className="mt-2 text-3xl font-bold tracking-tight text-white">
                Sign in
              </h2>

              <p className="mt-2 text-sm text-slate-500">
                Access your NightBreach learner account.
              </p>
            </div>

            {registered && (
              <div className="mb-5 rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-3 text-sm text-emerald-300">
                Account created successfully.
                Sign in to continue to onboarding.
              </div>
            )}

            {error && (
              <div className="mb-5 flex gap-3 rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-300">
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form
              onSubmit={handleSubmit}
              className="space-y-4"
            >
              <div>
                <label
                  htmlFor="username"
                  className="mb-2 block text-xs font-medium text-slate-400"
                >
                  Username
                </label>

                <div className="relative">
                  <User className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-600" />

                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    value={form.username}
                    onChange={updateField}
                    className="nb-input w-full rounded-xl py-3 pl-10 pr-3 text-sm"
                    placeholder="your-username"
                  />
                </div>
              </div>

              <div>
                <div className="mb-2 flex items-center justify-between">
                  <label
                    htmlFor="password"
                    className="text-xs font-medium text-slate-400"
                  >
                    Password
                  </label>

                  <Link
                    to="/forgot-password"
                    className="text-xs text-blue-400 hover:text-blue-300"
                  >
                    Forgot password?
                  </Link>
                </div>

                <div className="relative">
                  <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-600" />

                  <input
                    id="password"
                    name="password"
                    type={
                      showPassword
                        ? 'text'
                        : 'password'
                    }
                    autoComplete="current-password"
                    value={form.password}
                    onChange={updateField}
                    className="nb-input w-full rounded-xl py-3 pl-10 pr-11 text-sm"
                    placeholder="Your password"
                  />

                  <button
                    type="button"
                    onClick={() =>
                      setShowPassword(
                        (value) => !value,
                      )
                    }
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-300"
                    aria-label={
                      showPassword
                        ? 'Hide password'
                        : 'Show password'
                    }
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="nb-button-primary flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  <>
                    Sign in
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>
            </form>

            <div className="my-6 flex items-center gap-3">
              <div className="h-px flex-1 bg-slate-800" />
              <span className="text-[10px] uppercase tracking-wider text-slate-700">
                or
              </span>
              <div className="h-px flex-1 bg-slate-800" />
            </div>

            <p className="text-center text-sm text-slate-500">
              New to NightBreach?{' '}
              <Link
                to="/register"
                className="font-semibold text-blue-400 hover:text-blue-300"
              >
                Create an account
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
