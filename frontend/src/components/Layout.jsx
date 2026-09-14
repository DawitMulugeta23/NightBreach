import React from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Navbar from './Navbar'
import Footer from './Footer'

function Layout() {
  const { pathname } = useLocation()
  // Lesson pages are full-height workspaces — footer would push them past the viewport.
  const hideFooter = pathname.startsWith('/learning/lessons/')

  return (
    <div className="min-h-screen bg-white dark:bg-neutral-950 text-neutral-900 dark:text-neutral-100 flex flex-col">
      <Navbar />
      <main className="flex-1 min-h-0">
        <Outlet />
      </main>
      {!hideFooter && <Footer />}
    </div>
  )
}

export default Layout
