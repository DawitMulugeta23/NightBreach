import {
  createBrowserRouter,
  Navigate,
} from 'react-router-dom'

import AppLayout from '../layouts/AppLayout.jsx'

import LandingPage from '../pages/Landing/LandingPage.jsx'
import LoginPage from '../pages/Auth/LoginPage.jsx'
import RegisterPage from '../pages/Auth/RegisterPage.jsx'

import DashboardPage from '../pages/Dashboard/DashboardPage.jsx'
import LearningPage from '../pages/Learning/LearningPage.jsx'
import LearningPathPage from '../pages/LearningPath/LearningPathPage.jsx'
import ModulePage from '../pages/Module/ModulePage.jsx'
import RoomPage from '../pages/Room/RoomPage.jsx'
import LessonPage from '../pages/Lesson/LessonPage.jsx'
import PracticePage from '../pages/Practice/PracticePage.jsx'
import CTFPage from '../pages/CTF/CTFPage.jsx'
import ProgressPage from '../pages/Progress/ProgressPage.jsx'
import RecommendationsPage from '../pages/Recommendations/RecommendationsPage.jsx'
import SettingsPage from '../pages/Settings/SettingsPage.jsx'
import OnboardingWelcomePage from '../pages/Onboarding/OnboardingWelcomePage.jsx'
import OnboardingAssessmentPage from '../pages/Onboarding/OnboardingAssessmentPage.jsx'
import OnboardingResultPage from '../pages/Onboarding/OnboardingResultPage.jsx'
import ProtectedRoute from './ProtectedRoute.jsx'

const router = createBrowserRouter([
  /*
   * Public
   */
  {
    path: '/',
    element: <LandingPage />,
  },

  /*
   * Authentication
   */
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },

  /*
   * Protected learner application
   */
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppLayout />,
        children: [
          {
            path: '/onboarding',
            element: <OnboardingWelcomePage />,
          },
          {
            path: '/onboarding/assessment',
            element: <OnboardingAssessmentPage />,
          },
          {
            path: '/onboarding/result',
            element: <OnboardingResultPage />,
          },
          {
            path: '/dashboard',
            element: <DashboardPage />,
          },
          {
            path: '/learning',
            element: <LearningPage />,
          },
          {
            path: '/learning-paths/:learningPathId',
            element: <LearningPathPage />,
          },
          {
            path: '/modules/:moduleId',
            element: <ModulePage />,
          },
          {
            path: '/rooms/:roomId',
            element: <RoomPage />,
          },
          {
            path: '/lessons/:lessonId',
            element: <LessonPage />,
          },
          {
            path: '/practice/:activityId',
            element: <PracticePage />,
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
          {
            path: '/learning-paths',
            element: (
              <Navigate
                to="/learning"
                replace
              />
            ),
          },
        ],
      },
    ],
  },
])

export default router
