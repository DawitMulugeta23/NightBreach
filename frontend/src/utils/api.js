const API_BASE = '/api'

export async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`
  const defaultOptions = {
    headers: { 'Content-Type': 'application/json' },
  }
  const response = await fetch(url, { ...defaultOptions, ...options })
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `Request failed: ${response.status}`)
  }
  return response.json()
}

export const authApi = {
  login: (username, password) =>
    apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),
  register: (username, email, password) =>
    apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    }),
  getCurrentUser: (token) =>
    apiRequest(`/auth/me?token=${encodeURIComponent(token)}`),
}

export const learningApi = {
  listPaths: (token) =>
    apiRequest(`/learning/paths?token=${encodeURIComponent(token)}`),
  getPath: (pathId, token) =>
    apiRequest(`/learning/paths/${pathId}?token=${encodeURIComponent(token)}`),
  listRoomLessons: (roomId, token) =>
    apiRequest(`/learning/rooms/${roomId}/lessons?token=${encodeURIComponent(token)}`),
  getLesson: (lessonId, token) =>
    apiRequest(`/learning/lessons/${lessonId}?token=${encodeURIComponent(token)}`),
  startQuestion: (questionId, token) =>
    apiRequest(`/learning/questions/${questionId}/start?token=${encodeURIComponent(token)}`, {
      method: 'POST',
    }),
  submitAnswer: (questionId, answer, token) =>
    apiRequest(`/learning/questions/${questionId}/submit?token=${encodeURIComponent(token)}`, {
      method: 'POST',
      body: JSON.stringify({ answer }),
    }),
  getStats: (token) =>
    apiRequest(`/learning/stats?token=${encodeURIComponent(token)}`),
}

export const tokenStorage = {
  get: () => localStorage.getItem('roha_token'),
  set: (token) => localStorage.setItem('roha_token', token),
  remove: () => localStorage.removeItem('roha_token'),
  exists: () => !!localStorage.getItem('roha_token'),
}
