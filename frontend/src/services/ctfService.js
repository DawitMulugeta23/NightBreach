import {
  apiGet,
  apiPost,
} from '../api/client.js'

export function listCTFChallenges({
  groupId,
} = {}) {
  const query = groupId
    ? `?group_id=${encodeURIComponent(groupId)}`
    : ''

  return apiGet(
    `/ctf/challenges${query}`,
  )
}

export function getCTFChallenge(challengeId) {
  return apiGet(
    `/ctf/challenges/${challengeId}`,
  )
}

export function getCTFChallengeBySlug(slug) {
  return apiGet(
    `/ctf/challenges/slug/${encodeURIComponent(slug)}`,
  )
}

export function startCTFAttempt(
  challengeId,
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
    `/ctf/challenges/${challengeId}/attempts`,
    body,
  )
}

export function startCTFAttemptProgress(
  attemptId,
) {
  return apiPost(
    `/ctf/attempts/${attemptId}/start`,
  )
}

export function getCTFAttempt(attemptId) {
  return apiGet(
    `/ctf/attempts/${attemptId}`,
  )
}

export function listCTFAttempts(challengeId) {
  return apiGet(
    `/ctf/challenges/${challengeId}/attempts`,
  )
}

export function submitCTFAttempt(
  attemptId,
  submissionValue,
) {
  return apiPost(
    `/ctf/attempts/${attemptId}/submit`,
    {
      submission_value: submissionValue,
    },
  )
}

export function listCTFSubmissions(attemptId) {
  return apiGet(
    `/ctf/attempts/${attemptId}/submissions`,
  )
}

export function markCTFEnvironmentFailed(
  attemptId,
) {
  return apiPost(
    `/ctf/attempts/${attemptId}/environment-failed`,
  )
}
