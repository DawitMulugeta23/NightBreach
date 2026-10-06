const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  'http://127.0.0.1:8000/api/v1'

const SESSION_STORAGE_KEY = 'nightbreach_session'

export function getStoredSession() {
  return localStorage.getItem(SESSION_STORAGE_KEY)
}

export function setStoredSession(session) {
  if (!session) {
    localStorage.removeItem(SESSION_STORAGE_KEY)
    return
  }

  localStorage.setItem(
    SESSION_STORAGE_KEY,
    session,
  )
}

export function clearStoredSession() {
  localStorage.removeItem(SESSION_STORAGE_KEY)
}

async function parseResponse(response) {
  const contentType =
    response.headers.get('content-type') || ''

  if (contentType.includes('application/json')) {
    return response.json()
  }

  const text = await response.text()

  return text ? { message: text } : null
}

function getErrorMessage(payload, fallback) {
  if (!payload) {
    return fallback
  }

  if (typeof payload === 'string') {
    return payload
  }

  if (typeof payload.detail === 'string') {
    return payload.detail
  }

  if (typeof payload.message === 'string') {
    return payload.message
  }

  if (typeof payload.error === 'string') {
    return payload.error
  }

  if (Array.isArray(payload.detail)) {
    return payload.detail
      .map((item) => {
        if (typeof item === 'string') {
          return item
        }

        return (
          item?.msg ||
          item?.message ||
          JSON.stringify(item)
        )
      })
      .join(', ')
  }

  return fallback
}

export async function apiRequest(
  path,
  {
    method = 'GET',
    body,
    headers = {},
    ...options
  } = {},
) {
  const session = getStoredSession()

  const requestHeaders = {
    Accept: 'application/json',
    ...headers,
  }

  if (body !== undefined) {
    requestHeaders['Content-Type'] =
      'application/json'
  }

  if (session) {
    requestHeaders.Authorization =
      `Bearer ${session}`
  }

  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      method,
      headers: requestHeaders,
      body:
        body === undefined
          ? undefined
          : JSON.stringify(body),
      ...options,
    },
  )

  const data = await parseResponse(response)

  if (!response.ok) {
    const error = new Error(
      getErrorMessage(
        data,
        `Request failed with status ${response.status}`,
      ),
    )

    error.status = response.status
    error.data = data

    throw error
  }

  return data
}

export function apiGet(path, options = {}) {
  return apiRequest(path, {
    ...options,
    method: 'GET',
  })
}

export function apiPost(
  path,
  body,
  options = {},
) {
  return apiRequest(path, {
    ...options,
    method: 'POST',
    body,
  })
}

export function apiPut(
  path,
  body,
  options = {},
) {
  return apiRequest(path, {
    ...options,
    method: 'PUT',
    body,
  })
}

export function apiPatch(
  path,
  body,
  options = {},
) {
  return apiRequest(path, {
    ...options,
    method: 'PATCH',
    body,
  })
}

export function apiDelete(path, options = {}) {
  return apiRequest(path, {
    ...options,
    method: 'DELETE',
  })
}

export { API_BASE_URL }
