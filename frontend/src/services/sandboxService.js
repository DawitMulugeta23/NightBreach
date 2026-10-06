import {
  apiGet,
  apiPost,
} from '../api/client.js'

export function createSandboxEnvironment(
  activityId,
) {
  return apiPost(
    '/sandbox/environments',
    {
      activity_id: activityId,
    },
  )
}

export function getSandboxEnvironment(
  environmentId,
) {
  return apiGet(
    `/sandbox/environments/${environmentId}`,
  )
}

export function provisionSandboxEnvironment(
  environmentId,
  {
    networks,
    machines,
  },
) {
  return apiPost(
    `/sandbox/environments/${environmentId}/provision`,
    {
      networks,
      machines,
    },
  )
}

export function startSandboxEnvironment(
  environmentId,
) {
  return apiPost(
    `/sandbox/environments/${environmentId}/start`,
  )
}

export function resetSandboxEnvironment(
  environmentId,
) {
  return apiPost(
    `/sandbox/environments/${environmentId}/reset`,
  )
}

export function stopSandboxEnvironment(
  environmentId,
) {
  return apiPost(
    `/sandbox/environments/${environmentId}/stop`,
  )
}

export function validateSandboxEnvironment(
  environmentId,
) {
  return apiPost(
    `/sandbox/environments/${environmentId}/validate`,
  )
}

export function terminateSandboxEnvironment(
  environmentId,
) {
  return apiPost(
    `/sandbox/environments/${environmentId}/terminate`,
  )
}
