import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import LoadingSpinner from './LoadingSpinner'

function ProtectedRoute({ children, requireOnboarding = true }) {
  const { user, isAuthenticated, loading } = useAuth()

  if (loading) return <LoadingSpinner />

  if (!isAuthenticated) return <Navigate to="/login" replace />

  // Users who haven't finished the placement quiz are routed there first.
  // (undefined = backend didn't report it — don't loop, just let them through.)
  if (
    requireOnboarding &&
    user &&
    user.onboarding_quiz_completed === false
  ) {
    return <Navigate to="/onboarding" replace />
  }

  return children
}

export default ProtectedRoute
