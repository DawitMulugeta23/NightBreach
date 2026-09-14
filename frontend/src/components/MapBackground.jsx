import React from 'react'

/**
 * Renders the Ethiopia map as a decorative background element.
 * `position`: 'top-right' | 'top-left' | 'center-left' | 'center-right' | 'full'
 * `opacity`: number (0-100)
 */
function MapBackground({ position = 'top-right', opacity = 20, className = '' }) {
  const positions = {
    'top-right': 'absolute -top-20 right-0 w-[500px] sm:w-[600px] md:w-[700px] lg:w-[900px]',
    'top-left': 'absolute -top-20 left-0 w-[500px] sm:w-[600px] md:w-[700px] lg:w-[900px]',
    'center-left': 'absolute -left-40 top-1/2 -translate-y-1/2 w-[500px] sm:w-[600px] md:w-[700px] lg:w-[900px]',
    'center-right': 'absolute -right-40 top-1/2 -translate-y-1/2 w-[500px] sm:w-[600px] md:w-[700px] lg:w-[900px]',
    'full': 'absolute inset-0 w-full h-full object-cover',
  }

  const isFull = position === 'full'

  return (
    <img
      src="/ethioctf.jpeg"
      alt=""
      aria-hidden="true"
      className={`${isFull ? 'absolute inset-0 w-full h-full object-cover' : positions[position]} pointer-events-none select-none ${className}`}
      style={{ opacity: opacity / 100 }}
    />
  )
}

export default MapBackground
