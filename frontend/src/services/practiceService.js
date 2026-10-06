import {
  apiGet,
  apiPost,
} from '../api/client.js'

export function startPracticeAttempt(
  activityId,
  {
    environmentId,
    sessionId,
  } = {},
) {
  const body = {}

  if (environmentId) {
    body.environment_id = environmentId
  }

  if (sessionId) {
    body.session_id = sessionId
  }

  return apiPost(
    `/practice/activities/${activityId}/attempts`,
    body,
  )
}

export function getPracticeAttempt(attemptId) {
  return apiGet(
    `/practice/attempts/${attemptId}`,
  )
}

export function listPracticeAttempts(activityId) {
  return apiGet(
    `/practice/activities/${activityId}/attempts`,
  )
}

export function submitPracticeAttempt(
  attemptId,
  submission,
) {
  return apiPost(
    `/practice/attempts/${attemptId}/submit`,
    {
      submission,
    },
  )
}
