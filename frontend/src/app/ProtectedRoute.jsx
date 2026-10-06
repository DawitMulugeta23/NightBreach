import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { useAuth } from '../context/useAuth.js'

function ProtectedRoute() {
  const {
    loading,
    isAuthenticated,
  } = useAuth()

  const location = useLocation()

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#020711]">
        <div className="text-sm text-slate-400">
          Loading NightBreach...
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: location.pathname,
        }}
      />
    )
  }

  return <Outlet />
}

export default ProtectedRoute
