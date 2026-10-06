import {
  AlertCircle,
  ArrowRight,
  Eye,
  EyeOff,
  Loader2,
  Lock,
  Mail,
  User,
} from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import NightBreachLogo from '../../components/common/NightBreachLogo.jsx'
import { useAuth } from '../../context/useAuth.js'
import nightbreachAssets from '../../config/nightbreachAssets.js'

function RegisterPage() {
  const navigate = useNavigate()
  const { register } = useAuth()

  const [form, setForm] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
  })

  const [showPassword, setShowPassword] =
    useState(false)

  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false)

  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

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

    if (
      !form.email.trim() ||
      !form.username.trim() ||
      !form.password
    ) {
      setError(
        'Email, username, and password are required.',
      )
      return
    }

    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setLoading(true)

    try {
      await register({
        email: form.email.trim(),
        username: form.username.trim(),
        password: form.password,
      })

      navigate('/login', {
        replace: true,
        state: {
          registered: true,
          username: form.username.trim(),
        },
      })
    } catch (requestError) {
      setError(
        requestError.message ||
          'Registration failed. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#020711] text-slate-100">
      <div className="grid min-h-screen lg:grid-cols-[1.05fr_0.95fr]">

        <div className="relative hidden overflow-hidden border-r border-slate-800/70 lg:block">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(0,126,255,.16),transparent_35%),radial-gradient(circle_at_70%_80%,rgba(0,200,255,.08),transparent_35%)]" />

          <img
            src={nightbreachAssets.illustrations.onboarding}
            alt=""
            className="absolute inset-0 h-full w-full object-cover opacity-25"
          />

          <div className="relative flex h-full flex-col justify-between p-10">
            <NightBreachLogo />

            <div className="max-w-lg">
              <div className="mb-4 text-xs font-semibold uppercase tracking-[0.18em] text-blue-400">
                Start your journey
              </div>

              <h1 className="text-4xl font-bold tracking-tight text-white">
                Build practical cybersecurity skills.
              </h1>

              <p className="mt-5 max-w-md text-sm leading-7 text-slate-400">
                Learn concepts, practice with controlled
                environments, solve challenges, and
                progressively develop practical capability.
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
                Create account
              </div>

              <h2 className="mt-2 text-3xl font-bold tracking-tight text-white">
                Join NightBreach
              </h2>

              <p className="mt-2 text-sm text-slate-500">
                Create your learner account to begin.
              </p>
            </div>

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
                  htmlFor="email"
                  className="mb-2 block text-xs font-medium text-slate-400"
                >
                  Email
                </label>

                <div className="relative">
                  <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-600" />

                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    value={form.email}
                    onChange={updateField}
                    className="nb-input w-full rounded-xl py-3 pl-10 pr-3 text-sm"
                    placeholder="you@example.com"
                  />
                </div>
              </div>

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
                <label
                  htmlFor="password"
                  className="mb-2 block text-xs font-medium text-slate-400"
                >
                  Password
                </label>

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
                    autoComplete="new-password"
                    value={form.password}
                    onChange={updateField}
                    className="nb-input w-full rounded-xl py-3 pl-10 pr-11 text-sm"
                    placeholder="Create a password"
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

              <div>
                <label
                  htmlFor="confirmPassword"
                  className="mb-2 block text-xs font-medium text-slate-400"
                >
                  Confirm password
                </label>

                <div className="relative">
                  <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-600" />

                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={
                      showConfirmPassword
                        ? 'text'
                        : 'password'
                    }
                    autoComplete="new-password"
                    value={form.confirmPassword}
                    onChange={updateField}
                    className="nb-input w-full rounded-xl py-3 pl-10 pr-11 text-sm"
                    placeholder="Repeat your password"
                  />

                  <button
                    type="button"
                    onClick={() =>
                      setShowConfirmPassword(
                        (value) => !value,
                      )
                    }
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-300"
                    aria-label={
                      showConfirmPassword
                        ? 'Hide password'
                        : 'Show password'
                    }
                  >
                    {showConfirmPassword ? (
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
                    Creating account...
                  </>
                ) : (
                  <>
                    Create account
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>
            </form>

            <p className="mt-7 text-center text-sm text-slate-500">
              Already have an account?{' '}
              <Link
                to="/login"
                className="font-semibold text-blue-400 hover:text-blue-300"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
