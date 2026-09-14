import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Home from './pages/Home'
import LearningPaths from './pages/LearningPaths'
import LearningRoom from './pages/LearningRoom'
import LessonDetail from './pages/LessonDetail'
import Challenges from './pages/Challenges'
import Leaderboard from './pages/Leaderboard'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Arena from './pages/Arena'
import Settings from './pages/Settings'

function App() {
  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3500,
          style: {
            background: '#1a1a1a',
            color: '#f3f4f6',
            border: '1px solid #2a2a2a',
            fontSize: '0.875rem',
            padding: '12px 16px',
            borderRadius: '0.75rem',
            boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
          },
          success: {
            iconTheme: {
              primary: '#34d399',
              secondary: '#0a0a0a',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#0a0a0a',
            },
            style: {
              background: '#1a1a1a',
              color: '#fecaca',
              border: '1px solid #7f1d1d',
            },
          },
          loading: {
            iconTheme: {
              primary: '#34d399',
              secondary: '#0a0a0a',
            },
          },
        }}
      />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="learning-paths" element={<LearningPaths />} />
          <Route
            path="learning/paths/:pathId/rooms/:roomId"
            element={
              <ProtectedRoute>
                <LearningRoom />
              </ProtectedRoute>
            }
          />
          <Route
            path="learning/lessons/:lessonId"
            element={
              <ProtectedRoute>
                <LessonDetail />
              </ProtectedRoute>
            }
          />
          <Route path="challenges" element={<Challenges />} />
          <Route path="leaderboard" element={<Leaderboard />} />
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
          <Route
            path="dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="arena"
            element={
              <ProtectedRoute>
                <Arena />
              </ProtectedRoute>
            }
          />
          <Route
            path="settings"
            element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            }
          />
        </Route>
      </Routes>
    </>
  )
}

export default App
