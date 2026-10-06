import { API_BASE_URL, apiGet, apiPost } from './client.js'

export const launchLab = (slug) =>
  apiPost(`/sandbox/labs/${encodeURIComponent(slug)}/launch`, {})

export const getLabEnvironment = (environmentId) =>
  apiGet(`/sandbox/environments/${environmentId}/lab`)

const environmentAction = (name) => (environmentId) =>
  apiPost(`/sandbox/environments/${environmentId}/${name}`, {})

export const startEnvironment = environmentAction('start')
export const stopEnvironment = environmentAction('stop')
export const resetEnvironment = environmentAction('reset')
export const terminateEnvironment = environmentAction('terminate')

export const createTerminalSession = (environmentId, machineName) =>
  apiPost(
    `/sandbox/environments/${environmentId}/machines/${encodeURIComponent(machineName)}/terminal-sessions`,
    {},
  )

export const terminalSocketUrl = (sessionId) =>
  `${API_BASE_URL.replace(/^http/, 'ws')}/sandbox/terminal/${sessionId}`
