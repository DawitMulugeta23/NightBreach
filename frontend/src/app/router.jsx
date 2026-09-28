import { createBrowserRouter } from 'react-router-dom'

import AppLayout from '../layouts/AppLayout.jsx'
import LandingPage from '../pages/Landing/LandingPage.jsx'
import DashboardPage from '../pages/Dashboard/DashboardPage.jsx'
import CTFPage from '../pages/CTF/CTFPage.jsx'
import ProgressPage from '../pages/Progress/ProgressPage.jsx'
import RecommendationsPage from '../pages/Recommendations/RecommendationsPage.jsx'
import SettingsPage from '../pages/Settings/SettingsPage.jsx'

function PlaceholderPage({ title }) {
  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <h1 className="text-3xl font-bold text-white">{title}</h1>
      <p className="mt-2 text-slate-400">
        This NightBreach area will be implemented next.
      </p>
    </div>
  )
}

const router = createBrowserRouter([
  {
    path: '/',
    element: <LandingPage />,
  },
  {
    element: <AppLayout />,
    children: [
      {
        path: '/dashboard',
        element: <DashboardPage />,
      },
      {
        path: '/learning',
        element: <PlaceholderPage title="Learning" />,
      },
      {
        path: '/ctf',
        element: <CTFPage />,
      },
      {
        path: '/progress',
        element: <ProgressPage />,
      },
      {
        path: '/recommendations',
        element: <RecommendationsPage />,
      },
      {
        path: '/settings',
        element: <SettingsPage />,
      },
    ],
  },
])

export default router
