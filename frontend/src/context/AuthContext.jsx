import React, { createContext, useContext, useState, useEffect } from 'react'
import { tokenStorage, authApi } from '../utils/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = tokenStorage.get()
    if (token) {
      authApi.getCurrentUser(token)
        .then(setUser)
        .catch(() => {
          tokenStorage.remove()
          setUser(null)
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = (token, userData) => {
    tokenStorage.set(token)
    setUser(userData)
  }

  const logout = () => {
    tokenStorage.remove()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
