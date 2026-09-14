import React from 'react'

function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center gap-4">
      <i className="fas fa-spinner fa-spin text-4xl text-emerald-400"></i>
      <p className="text-sm text-neutral-600 dark:text-neutral-400">{message}</p>
    </div>
  )
}

export default LoadingSpinner
