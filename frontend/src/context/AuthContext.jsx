import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  getCurrentIdentity,
  loginAccount,
  logoutAccount,
  registerAccount,
} from '../services/authService.js'

import { AuthContext } from './authContext.js'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const refreshIdentity = useCallback(async () => {
    try {
      const response =
        await getCurrentIdentity()

      const identity =
        response?.data ??
        response

      setUser(identity)

      return identity
    } catch (error) {
      if (
        error.status === 401 ||
        error.status === 403
      ) {
        setUser(null)
      }

      return null
    }
  }, [])

  useEffect(() => {
    let mounted = true

    async function initialize() {
      try {
        const identity =
          await refreshIdentity()

        if (mounted) {
          setUser(identity)
        }
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }

    initialize()

    return () => {
      mounted = false
    }
  }, [refreshIdentity])

  const register = useCallback(
    async (credentials) => {
      return registerAccount(credentials)
    },
    [],
  )

  const login = useCallback(
    async (credentials) => {
      const response =
        await loginAccount(credentials)

      const identity =
        response?.data ??
        response

      const currentUser =
        await refreshIdentity()

      setUser(currentUser || identity)

      return response
    },
    [refreshIdentity],
  )

  const logout = useCallback(async () => {
    try {
      await logoutAccount()
    } finally {
      setUser(null)
    }
  }, [])

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      register,
      login,
      logout,
      refreshIdentity,
    }),
    [
      user,
      loading,
      register,
      login,
      logout,
      refreshIdentity,
    ],
  )

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
