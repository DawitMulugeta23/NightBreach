import React, { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { learningApi, tokenStorage } from '../utils/api'
import { useAuth } from '../context/AuthContext'
import MapBackground from '../components/MapBackground'
import Breadcrumb from '../components/Breadcrumb'
import LoadingSpinner from '../components/LoadingSpinner'
import Terminal from '../components/Terminal'

const DEFAULT_SPLIT = 50
const MIN_SPLIT = 25
const MAX_SPLIT = 75

function LessonDetail() {
  const { lessonId } = useParams()
  const navigate = useNavigate()
  const { isAuthenticated, loading: authLoading } = useAuth()

  const [lesson, setLesson] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [answers, setAnswers] = useState({})
  const [feedback, setFeedback] = useState({})
  const [submitting, setSubmitting] = useState({})
  const [showTerminal, setShowTerminal] = useState(false)
  const [terminalKey, setTerminalKey] = useState(0)
  const [splitPercent, setSplitPercent] = useState(DEFAULT_SPLIT)
  const [isDragging, setIsDragging] = useState(false)
  const containerRef = useRef(null)

  const loadLesson = () => {
    const token = tokenStorage.get()
    if (!token) return
    setLoading(true)
    learningApi
      .getLesson(lessonId, token)
      .then(setLesson)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated) return navigate('/login')
    loadLesson()
    setAnswers({})
    setFeedback({})
    setShowTerminal(false)
    setSplitPercent(DEFAULT_SPLIT)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lessonId, isAuthenticated, authLoading])

  const handleMouseDown = useCallback((e) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  useEffect(() => {
    if (!isDragging) return

    const handleMove = (e) => {
      const container = containerRef.current
      if (!container) return
      const rect = container.getBoundingClientRect()
      const relativeX = e.clientX - rect.left
      let percent = (relativeX / rect.width) * 100
      percent = Math.max(MIN_SPLIT, Math.min(MAX_SPLIT, percent))
      setSplitPercent(percent)
    }

    const handleUp = () => setIsDragging(false)

    window.addEventListener('mousemove', handleMove)
    window.addEventListener('mouseup', handleUp)
    document.body.style.userSelect = 'none'
    document.body.style.cursor = 'col-resize'

    return () => {
      window.removeEventListener('mousemove', handleMove)
      window.removeEventListener('mouseup', handleUp)
      document.body.style.userSelect = ''
      document.body.style.cursor = ''
    }
  }, [isDragging])

  const handleSubmit = async (questionId) => {
    const answer = (answers[questionId] || '').trim()
    if (!answer) return

    setSubmitting((s) => ({ ...s, [questionId]: true }))
    const token = tokenStorage.get()

    try {
      const result = await learningApi.submitAnswer(questionId, answer, token)
      if (result.correct) {
        setFeedback((f) => ({ ...f, [questionId]: { type: 'success', text: 'Correct!' } }))
        toast.success('Correct!')
        const updated = await learningApi.getLesson(lessonId, token)
        setLesson(updated)
      } else {
        setFeedback((f) => ({ ...f, [questionId]: { type: 'error', text: 'Incorrect. Try again.' } }))
        toast.error('Incorrect. Try again.')
      }
    } catch (err) {
      setFeedback((f) => ({ ...f, [questionId]: { type: 'error', text: err.message } }))
    } finally {
      setSubmitting((s) => ({ ...s, [questionId]: false }))
    }
  }

  const handleStartMachine = () => {
    setShowTerminal(true)
    setTerminalKey((k) => k + 1)
  }

  const goToLesson = (id) => {
    if (id) navigate(`/learning/lessons/${id}`)
  }

  if (authLoading || loading) return <LoadingSpinner message="Loading lesson..." />

  if (error) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center px-4">
        <div className="text-center">
          <i className="fas fa-circle-exclamation text-4xl text-red-400 mb-4"></i>
          <p className="text-red-400">{error}</p>
        </div>
      </div>
    )
  }

  const textBlocks = lesson?.blocks.filter((b) => b.type === 'text') || []
  const practiceBlocks = lesson?.blocks.filter((b) => b.type === 'practice') || []
  const hasTerminalQuestion = lesson?.questions.some((q) => q.question_type === 'terminal')
  const needsTerminal = practiceBlocks.length > 0 || hasTerminalQuestion

  // -------- LAYOUT A: no terminal --------
  if (!showTerminal) {
    return (
      <div className="relative w-full min-h-screen px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-8 md:py-12 overflow-hidden bg-white dark:bg-neutral-950">
        <MapBackground position="top-right" opacity={10} />
        <div className="relative max-w-7xl mx-auto">
          <Breadcrumb
            items={[
              { label: 'Learning Paths', to: '/learning-paths' },
              { label: lesson?.title },
            ]}
          />

          <div className="flex items-center justify-between flex-wrap gap-3 mb-6">
            <h1 className="text-2xl md:text-3xl font-bold text-neutral-900 dark:text-white flex items-center gap-3">
              <i className="fas fa-book-open text-emerald-400"></i>
              {lesson?.title}
            </h1>
            {lesson?.completed && (
              <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-xs font-bold uppercase tracking-wider">
                <i className="fas fa-check-circle"></i>
                Completed
              </span>
            )}
          </div>

          {needsTerminal && (
            <div className="mb-6 flex items-center gap-3 flex-wrap">
              <button
                onClick={handleStartMachine}
                className="inline-flex items-center gap-2 px-5 py-3 text-sm font-semibold rounded-xl bg-emerald-600 hover:bg-emerald-500 text-neutral-900 dark:text-white shadow-lg shadow-emerald-600/20 hover:shadow-emerald-500/40 transition-all duration-200"
              >
                <i className="fas fa-play"></i>
                Start Machine
              </button>
              <span className="text-xs text-neutral-500">
                <i className="fas fa-info-circle mr-1"></i>
                This lesson has hands-on practice. Start the machine to try commands.
              </span>
            </div>
          )}

          <LessonCard
            lesson={lesson}
            textBlocks={textBlocks}
            practiceBlocks={practiceBlocks}
            answers={answers}
            feedback={feedback}
            submitting={submitting}
            setAnswers={setAnswers}
            handleSubmit={handleSubmit}
          />
          <NavButtons lesson={lesson} goToLesson={goToLesson} />
        </div>
      </div>
    )
  }

  // -------- LAYOUT B: terminal shown, fixed viewport, resizable, content scrollable --------
  return (
    <div
      className="w-full bg-white dark:bg-neutral-950 flex flex-col overflow-hidden"
      style={{ height: 'calc(100vh - 72px)' }}
    >
      {/* Slim header bar — only breadcrumb + title. "Hide" is gone; use terminal's Close. */}
      <div className="flex-shrink-0 px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-2 border-b border-neutral-900 bg-white dark:bg-neutral-950">
        <Breadcrumb
          items={[
            { label: 'Learning Paths', to: '/learning-paths' },
            { label: lesson?.title },
          ]}
        />
        <div className="flex items-center gap-3 pb-1">
          <h1 className="text-base md:text-lg font-bold text-neutral-900 dark:text-white flex items-center gap-2">
            <i className="fas fa-book-open text-emerald-400"></i>
            {lesson?.title}
            {lesson?.completed && (
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-[10px] font-bold uppercase tracking-wider">
                <i className="fas fa-check-circle"></i>
                Completed
              </span>
            )}
          </h1>
        </div>
      </div>

      {/* Split area — fills remaining height */}
      <div
        ref={containerRef}
        className="flex-1 min-h-0 flex flex-row"
      >
        {/* LEFT — content column: internally scrollable, no outer padding at top/right */}
        <div
          className="min-w-0 overflow-y-auto"
          style={{
            flexBasis: `${splitPercent}%`,
            flexGrow: 0,
            flexShrink: 0,
            transition: isDragging ? 'none' : 'flex-basis 150ms ease-out',
          }}
        >
          <div className="px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-4">
            <LessonCard
              lesson={lesson}
              textBlocks={textBlocks}
              practiceBlocks={practiceBlocks}
              answers={answers}
              feedback={feedback}
              submitting={submitting}
              setAnswers={setAnswers}
              handleSubmit={handleSubmit}
            />
            <NavButtons lesson={lesson} goToLesson={goToLesson} />
          </div>
        </div>

        {/* RESIZE HANDLE */}
        <div
          onMouseDown={handleMouseDown}
          onTouchStart={handleMouseDown}
          className={`flex items-center justify-center cursor-col-resize select-none flex-shrink-0 transition-colors ${
            isDragging ? 'bg-emerald-500/40' : 'bg-transparent hover:bg-emerald-500/20'
          }`}
          style={{ width: '6px' }}
          title="Drag to resize"
        >
          <div
            className={`rounded-full transition-all ${
              isDragging ? 'bg-emerald-400 h-16 w-1' : 'bg-neutral-200 dark:bg-neutral-700 h-12 w-1 hover:bg-emerald-500'
            }`}
          />
        </div>

        {/* RIGHT — terminal column: flush to top/right/bottom, no padding */}
        <div
          className="min-w-0 min-h-0 flex flex-col"
          style={{
            flexBasis: `${100 - splitPercent}%`,
            flexGrow: 0,
            flexShrink: 0,
            transition: isDragging ? 'none' : 'flex-basis 150ms ease-out',
          }}
        >
          <Terminal
            key={terminalKey}
            autoStart={true}
            onClose={() => setShowTerminal(false)}
          />
        </div>
      </div>
    </div>
  )
}

// ---------------- Subcomponents ----------------

function LessonCard({
  lesson,
  textBlocks,
  practiceBlocks,
  answers,
  feedback,
  submitting,
  setAnswers,
  handleSubmit,
}) {
  return (
    <div
      className={`rounded-2xl overflow-hidden border-2 transition-colors ${
        lesson?.completed ? 'border-emerald-500/60' : 'border-neutral-300 dark:border-neutral-700'
      }`}
    >
      <div
        className={`px-6 py-4 border-b flex items-center justify-between ${
          lesson?.completed
            ? 'bg-emerald-950/50 border-emerald-800/50'
            : 'bg-neutral-100 dark:bg-neutral-800 border-neutral-300 dark:border-neutral-700'
        }`}
      >
        <div className="flex items-center gap-3">
          <i className={`fas ${lesson?.completed ? 'fa-check-circle' : 'fa-info-circle'} text-emerald-400`}></i>
          <span
            className={`text-sm font-semibold uppercase tracking-wider ${
              lesson?.completed ? 'text-emerald-300' : 'text-neutral-900 dark:text-white'
            }`}
          >
            {lesson?.completed ? 'Lesson Complete' : 'Lesson Content'}
          </span>
        </div>
        {lesson?.completed && <i className="fas fa-check-circle text-emerald-400 text-lg"></i>}
      </div>

      <div className="px-6 md:px-8 py-8 bg-neutral-50 text-neutral-900">
        {textBlocks.map((block, i) => (
          <div key={`t-${i}`} className={i > 0 ? 'mt-8 pt-8 border-t border-neutral-200' : ''}>
            {block.heading && (
              <h2 className="text-lg md:text-xl font-bold text-neutral-900 mb-4 flex items-center gap-3">
                <span className="w-1 h-6 bg-emerald-500 rounded-full"></span>
                {block.heading}
              </h2>
            )}
            <p className="text-sm md:text-base text-neutral-700 leading-relaxed whitespace-pre-wrap">
              {block.body}
            </p>
          </div>
        ))}

        {practiceBlocks.length > 0 && (
          <div className={textBlocks.length > 0 ? 'mt-8 pt-8 border-t border-neutral-200' : ''}>
            <h2 className="text-lg font-bold text-neutral-900 mb-4 flex items-center gap-3">
              <span className="w-1 h-6 bg-emerald-500 rounded-full"></span>
              Try It Yourself
            </h2>
            {practiceBlocks.map((block, i) => (
              <div key={`p-${i}`} className={i > 0 ? 'mt-6 pt-6 border-t border-neutral-200' : ''}>
                <p className="text-sm text-neutral-700 mb-3">{block.instructions}</p>
                {block.command && (
                  <code className="inline-block px-4 py-2.5 rounded-lg bg-neutral-50 dark:bg-neutral-900 border border-neutral-300 dark:border-neutral-700 text-emerald-400 text-sm font-mono">
                    $ {block.command}
                  </code>
                )}
              </div>
            ))}
          </div>
        )}

        {lesson?.questions.length > 0 && (
          <div
            className={
              textBlocks.length > 0 || practiceBlocks.length > 0
                ? 'mt-8 pt-8 border-t border-neutral-200'
                : ''
            }
          >
            <h2 className="text-lg font-bold text-neutral-900 mb-6 flex items-center gap-3">
              <span className="w-1 h-6 bg-emerald-500 rounded-full"></span>
              Questions
            </h2>

            <div className="space-y-5">
              {lesson.questions.map((q) => (
                <div
                  key={q.id}
                  className={`p-5 rounded-xl border ${
                    q.answered ? 'bg-emerald-50 border-emerald-300' : 'bg-white border-neutral-300'
                  }`}
                >
                  <div className="flex items-start gap-3 mb-4">
                    <div
                      className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold flex-shrink-0 ${
                        q.answered ? 'bg-emerald-500 text-neutral-900 dark:text-white' : 'bg-neutral-200 text-neutral-700'
                      }`}
                    >
                      {q.answered ? <i className="fas fa-check"></i> : q.order_index}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-neutral-900 leading-relaxed font-medium">{q.prompt}</p>
                      <div className="mt-2">
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase ${
                            q.question_type === 'terminal'
                              ? 'bg-blue-100 text-blue-700'
                              : 'bg-purple-100 text-purple-700'
                          }`}
                        >
                          <i className={`fas ${q.question_type === 'terminal' ? 'fa-terminal' : 'fa-text'} mr-1`}></i>
                          {q.question_type}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Your answer..."
                      value={answers[q.id] || ''}
                      onChange={(e) => setAnswers((a) => ({ ...a, [q.id]: e.target.value }))}
                      onKeyDown={(e) => e.key === 'Enter' && handleSubmit(q.id)}
                      disabled={q.answered}
                      className="flex-1 px-4 py-2 rounded-lg bg-neutral-100 border border-neutral-300 text-neutral-900 text-sm focus:outline-none focus:border-emerald-500 disabled:opacity-50"
                    />
                    <button
                      onClick={() => handleSubmit(q.id)}
                      disabled={q.answered || submitting[q.id]}
                      className="px-5 py-2 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-neutral-900 dark:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {submitting[q.id] ? (
                        <i className="fas fa-spinner fa-spin"></i>
                      ) : q.answered ? (
                        <>
                          <i className="fas fa-check"></i> Done
                        </>
                      ) : (
                        <>
                          <i className="fas fa-paper-plane"></i> Submit
                        </>
                      )}
                    </button>
                  </div>

                  {feedback[q.id] && (
                    <div
                      className={`mt-3 text-xs flex items-center gap-2 ${
                        feedback[q.id].type === 'success' ? 'text-emerald-700' : 'text-red-600'
                      }`}
                    >
                      <i
                        className={`fas ${
                          feedback[q.id].type === 'success' ? 'fa-check-circle' : 'fa-times-circle'
                        }`}
                      ></i>
                      {feedback[q.id].text}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function NavButtons({ lesson, goToLesson }) {
  return (
    <div className="flex items-center justify-between gap-3 mt-6">
      <button
        onClick={() => goToLesson(lesson?.prev_lesson_id)}
        disabled={!lesson?.prev_lesson_id}
        className={`inline-flex items-center gap-2 px-5 py-3 text-sm font-semibold rounded-xl transition-all ${
          lesson?.prev_lesson_id
            ? 'bg-neutral-100 dark:bg-neutral-800 hover:bg-neutral-200 dark:hover:bg-neutral-700 text-neutral-900 dark:text-white border border-neutral-300 dark:border-neutral-700'
            : 'bg-neutral-50 dark:bg-neutral-900 text-neutral-600 cursor-not-allowed border border-neutral-200 dark:border-neutral-800'
        }`}
      >
        <i className="fas fa-arrow-left"></i>
        Previous
      </button>

      <button
        onClick={() => goToLesson(lesson?.next_lesson_id)}
        disabled={!lesson?.next_lesson_id}
        className={`inline-flex items-center gap-2 px-5 py-3 text-sm font-semibold rounded-xl transition-all ${
          lesson?.next_lesson_id
            ? 'bg-emerald-600 hover:bg-emerald-500 text-neutral-900 dark:text-white shadow-lg shadow-emerald-600/20'
            : 'bg-neutral-50 dark:bg-neutral-900 text-neutral-600 cursor-not-allowed border border-neutral-200 dark:border-neutral-800'
        }`}
      >
        Next
        <i className="fas fa-arrow-right"></i>
      </button>
    </div>
  )
}

export default LessonDetail
