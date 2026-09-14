import React from 'react'
import { SITE } from '../utils/constants'

function Footer() {
  return (
    <footer className="w-full px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-6 md:py-8 border-t border-neutral-200 dark:border-neutral-800">
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-neutral-500">
        <div className="flex items-center gap-3">
          <img
            src="/dbu.jpg"
            alt="DBU"
            className="h-8 md:h-10 w-auto rounded border border-neutral-300 dark:border-neutral-700"
          />
          <span>&copy; {SITE.year} {SITE.name}</span>
        </div>
        <div className="flex flex-wrap items-center gap-4 md:gap-6">
          <a href="#" className="hover:text-neutral-300 transition-colors">
            <i className="fas fa-book mr-1"></i> Documentation
          </a>
          <a href="#" className="hover:text-neutral-300 transition-colors">
            <i className="fas fa-headset mr-1"></i> Support
          </a>
          <span className="text-neutral-600">
            <i className="fas fa-university text-emerald-400 mr-1"></i>
            {SITE.university} — {SITE.department}
          </span>
        </div>
      </div>
    </footer>
  )
}

export default Footer
