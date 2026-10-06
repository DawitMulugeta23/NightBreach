import {
  apiGet,
  apiPost,
  clearStoredSession,
  getStoredSession,
  setStoredSession,
} from '../api/client.js'

export async function registerAccount({
  email,
  username,
  password,
}) {
  return apiPost('/auth/register', {
    email,
    username,
    password,
  })
}

export async function loginAccount({
  username,
  password,
}) {
  const response = await apiPost('/auth/login', {
    username,
    password,
  })

  setStoredSession(response.access_token)

  return response
}

export async function getCurrentIdentity() {
  return apiGet('/auth/me')
}

export function logoutAccount() {
  clearStoredSession()
}

export function getStoredAuthSession() {
  return getStoredSession()
}

export function clearAuthSession() {
  clearStoredSession()
}
