import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { onboardingApi, authApi, tokenStorage } from '../utils/api'
import { useAuth } from '../context/AuthContext'

/**
 * Onboarding quiz (spec §4.1, Algorithm 1). Shown once after registration
 * (or after login for any user who hasn't completed it yet). The backend
 * scores the answers and assigns the user's progression_mode — the result
 * screen only reflects what the server decided.
 */
function OnboardingQuiz() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    const token = tokenStorage.get()
    if (!token) {
      navigate('/login', { replace: true })
      return
    }
    onboardingApi
      .getQuiz()
      .then(setQuestions)
      .catch((err) => {
        setError(err.message || 'Failed to load the quiz')
        toast.error(err.message || 'Failed to load the quiz')
      })
      .finally(() => setLoading(false))
  }, [navigate])

  const current = questions[step]

  const chooseOption = (optionId) => {
    setAnswers((prev) => ({ ...prev, [current.id]: optionId }))
  }

  const handleSubmit = async () => {
    const token = tokenStorage.get()
    if (!token) {
      navigate('/login', { replace: true })
      return
    }
    setSubmitting(true)
    setError('')
    try {
      const data = await onboardingApi.submitQuiz(answers, token)
      // Refresh the stored user so progression_mode is up to date app-wide.
      try {
        const userData = await authApi.getCurrentUser(token)
        login(token, userData)
      } catch { /* keep going with the submit result even if /me fails */ }
      setResult(data)
    } catch (err) {
      setError(err.message || 'Failed to submit the quiz')
    } finally {
      setSubmitting(false)
    }
  }

  const goNext = () => {
    if (step < questions.length - 1) setStep(step + 1)
    else handleSubmit()
  }

  const goBack = () => setStep((s) => Math.max(0, s - 1))

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-200px)] flex items-center justify-center px-4 py-14">
        <div className="flex flex-col items-center gap-4 text-neutral-600 dark:text-neutral-400">
          <i className="fas fa-spinner fa-spin text-3xl text-emerald-400"></i>
          <p className="text-sm">Preparing your placement quiz...</p>
        </div>
      </div>
    )
  }

  // ---- Result screen ----
  if (result) {
    const free = result.progression_mode === 'free'
    return (
      <div className="min-h-[calc(100vh-200px)] flex items-center justify-center px-4 py-14 relative overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img src="/ethioctf.jpeg" alt="" className="w-full h-full object-cover opacity-30" />
          <div className="absolute inset-0 bg-gradient-to-b from-neutral-950/70 via-neutral-950/50 to-neutral-950/70"></div>
        </div>

        <div className="relative z-10 w-full max-w-md text-center">
          <div className="relative mx-auto mb-6 w-20 h-20 md:w-24 md:h-24 flex items-center justify-center">
            <div className={`absolute inset-0 rounded-full blur-2xl ${free ? 'bg-emerald-500/30' : 'bg-amber-500/30'}`}></div>
            <i className={`fas ${free ? 'fa-gauge-high' : 'fa-route'} text-4xl md:text-5xl ${free ? 'text-emerald-400' : 'text-amber-400'} relative drop-shadow-[0_0_20px_rgba(52,211,153,0.5)]`}></i>
          </div>

          <h1 className="text-center text-sm md:text-base font-bold uppercase tracking-wide mb-6 text-neutral-900 dark:text-white flex items-center justify-center gap-2">
            <i className="fas fa-map-pin text-emerald-400"></i>
            NIGHTBREACH: ETHIOPIAN CYBER DEFENSE NETWORK
          </h1>

          <div className="bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-6 md:p-8 shadow-2xl shadow-black/50">
            <p className="text-xs uppercase tracking-widest text-neutral-500 mb-2">Your score</p>
            <p className="text-4xl font-extrabold text-emerald-400 mb-4">
              {Math.round(result.score * 100)}%
            </p>

            {free ? (
              <p className="text-sm text-neutral-600 dark:text-neutral-300 leading-relaxed">
                Strong fundamentals detected — you've been placed in{' '}
                <span className="text-emerald-400 font-semibold">free navigation</span>. All modules
                are open; move at your own pace.
              </p>
            ) : (
              <p className="text-sm text-neutral-600 dark:text-neutral-300 leading-relaxed">
                You've been placed in{' '}
                <span className="text-amber-400 font-semibold">guided mode</span>: modules unlock as
                you complete the previous one. Score{' '}
                <span className="text-emerald-400 font-semibold">90%+ first-attempt accuracy</span>{' '}
                across your recent modules and you'll be promoted to free navigation automatically.
              </p>
            )}

            <button
              onClick={() => navigate('/learning-paths')}
              className="btn-primary w-full py-3 text-sm mt-6 flex items-center justify-center gap-2"
            >
              <i className="fas fa-compass"></i> START LEARNING
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (error && questions.length === 0) {
    return (
      <div className="min-h-[calc(100vh-200px)] flex items-center justify-center px-4 py-14">
        <div className="text-center text-sm text-red-400 max-w-sm">
          <i className="fas fa-circle-exclamation text-3xl mb-3"></i>
          <p>{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="btn-primary px-6 py-2.5 text-sm mt-4 inline-flex items-center gap-2"
          >
            <i className="fas fa-rotate-right"></i> Retry
          </button>
        </div>
      </div>
    )
  }

  // ---- Question flow ----
  const answeredCount = Object.keys(answers).length
  const currentAnswered = !!answers[current?.id]

  return (
    <div className="min-h-[calc(100vh-200px)] flex items-center justify-center px-4 py-14 relative overflow-hidden">
      <div className="absolute inset-0 z-0">
        <img src="/ethioctf.jpeg" alt="" className="w-full h-full object-cover opacity-30" />
        <div className="absolute inset-0 bg-gradient-to-b from-neutral-950/70 via-neutral-950/50 to-neutral-950/70"></div>
      </div>

      <div className="relative z-10 w-full max-w-2xl">
        <h1 className="text-center text-sm md:text-base font-bold uppercase tracking-wide mb-2 text-neutral-900 dark:text-white flex items-center justify-center gap-2">
          <i className="fas fa-map-pin text-emerald-400"></i>
          NIGHTBREACH: ETHIOPIAN CYBER DEFENSE NETWORK
        </h1>
        <h2 className="text-center text-emerald-400 font-bold uppercase tracking-widest text-2xl md:text-3xl mb-3">
          PLACEMENT QUIZ
        </h2>
        <p className="text-center text-xs text-neutral-600 dark:text-neutral-400 mb-8">
          A few quick questions so we can tailor your path. You can't fail this — it just decides
          how guided your journey is.
        </p>

        {/* Progress bar */}
        <div className="flex items-center gap-3 mb-6">
          <div className="flex-1 h-1.5 rounded-full bg-neutral-200 dark:bg-neutral-800 overflow-hidden">
            <div
              className="h-full bg-emerald-400 transition-all duration-300"
              style={{ width: `${(answeredCount / questions.length) * 100}%` }}
            ></div>
          </div>
          <span className="text-xs text-neutral-500 font-mono">
            {step + 1} / {questions.length}
          </span>
        </div>

        <div className="bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-6 md:p-8 shadow-2xl shadow-black/50">
          <p className="text-xs uppercase tracking-widest text-neutral-500 mb-2">
            Question {step + 1}
          </p>
          <h3 className="text-lg font-bold text-neutral-900 dark:text-white mb-6 leading-snug">
            {current?.prompt}
          </h3>

          <div className="space-y-3">
            {current?.options.map((opt) => {
              const selected = answers[current.id] === opt.id
              return (
                <button
                  key={opt.id}
                  onClick={() => chooseOption(opt.id)}
                  className={`w-full text-left px-4 py-3.5 rounded-xl border text-sm transition-all flex items-center gap-3 ${
                    selected
                      ? 'border-emerald-400/60 bg-emerald-400/10 text-neutral-900 dark:text-white'
                      : 'border-neutral-200 dark:border-neutral-800 text-neutral-600 dark:text-neutral-300 hover:border-emerald-400/40 hover:bg-neutral-100 dark:hover:bg-neutral-800/60'
                  }`}
                >
                  <span
                    className={`w-5 h-5 rounded-full border flex-shrink-0 flex items-center justify-center text-[10px] ${
                      selected ? 'border-emerald-400 bg-emerald-400 text-neutral-950' : 'border-neutral-400 dark:border-neutral-600'
                    }`}
                  >
                    {selected && <i className="fas fa-check"></i>}
                  </span>
                  {opt.text}
                </button>
              )
            })}
          </div>

          {error && (
            <div className="text-red-400 text-xs mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
              <i className="fas fa-circle-exclamation mr-2"></i>
              {error}
            </div>
          )}

          <div className="flex items-center justify-between mt-8">
            <button
              onClick={goBack}
              disabled={step === 0 || submitting}
              className="text-xs text-neutral-600 dark:text-neutral-400 hover:text-emerald-400 transition-colors flex items-center gap-1.5 disabled:opacity-40 disabled:hover:text-neutral-600 dark:disabled:hover:text-neutral-400"
            >
              <i className="fas fa-arrow-left"></i> Back
            </button>
            <button
              onClick={goNext}
              disabled={!currentAnswered || submitting}
              className="btn-primary px-6 py-2.5 text-sm flex items-center gap-2 disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <i className="fas fa-spinner fa-spin"></i> SCORING...
                </>
              ) : step === questions.length - 1 ? (
                <>
                  FINISH <i className="fas fa-flag-checkered"></i>
                </>
              ) : (
                <>
                  NEXT <i className="fas fa-arrow-right"></i>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default OnboardingQuiz
