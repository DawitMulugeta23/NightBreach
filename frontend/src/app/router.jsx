import { createBrowserRouter } from 'react-router-dom'

import AppLayout from '../layouts/AppLayout.jsx'
import PlaceholderPage from '../pages/PlaceholderPage.jsx'
import LandingPage from '../pages/Landing/LandingPage.jsx'
import DashboardPage from '../pages/Dashboard/DashboardPage.jsx'
import CTFPage from '../pages/CTF/CTFPage.jsx'
import ProgressPage from '../pages/Progress/ProgressPage.jsx'
import RecommendationsPage from '../pages/Recommendations/RecommendationsPage.jsx'
import SettingsPage from '../pages/Settings/SettingsPage.jsx'

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
