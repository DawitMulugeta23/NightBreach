import {
  apiGet,
} from '../api/client.js'

export function listLearningPaths() {
  return apiGet('/learning-paths')
}

export function getLearningPath(learningPathId) {
  return apiGet(
    `/learning-paths/${learningPathId}`,
  )
}

export function getModule(moduleId) {
  return apiGet(
    `/modules/${moduleId}`,
  )
}

export function getRoom(roomId) {
  return apiGet(
    `/rooms/${roomId}`,
  )
}

export function getLesson(lessonId) {
  return apiGet(
    `/lessons/${lessonId}`,
  )
}
