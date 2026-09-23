const API_BASE = '/api'

export async function apiRequest(endpoint, options = {}, token = null) {
  const url = `${API_BASE}${endpoint}`
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const response = await fetch(url, { ...options, headers })
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
  getCurrentUser: (token) => apiRequest('/auth/me', {}, token),
}

export const learningApi = {
  listPaths: (token) => apiRequest('/learning/paths', {}, token),
  getPath: (pathId, token) => apiRequest(`/learning/paths/${pathId}`, {}, token),
  listRoomLessons: (roomId, token) => apiRequest(`/learning/rooms/${roomId}/lessons`, {}, token),
  getLesson: (lessonId, token) => apiRequest(`/learning/lessons/${lessonId}`, {}, token),
  startQuestion: (questionId, token) =>
    apiRequest(`/learning/questions/${questionId}/start`, { method: 'POST' }, token),
  submitAnswer: (questionId, answer, token) =>
    apiRequest(`/learning/questions/${questionId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answer }),
    }, token),
  getStats: (token) => apiRequest('/learning/stats', {}, token),
}

export const tokenStorage = {
  get: () => localStorage.getItem('roha_token'),
  set: (token) => localStorage.setItem('roha_token', token),
  remove: () => localStorage.removeItem('roha_token'),
  exists: () => !!localStorage.getItem('roha_token'),
}
