import {
  apiGet,
  apiPost,
} from '../api/client.js'

export function getLessonProgress(lessonId) {
  return apiGet(
    `/progress/lessons/${lessonId}`,
  )
}

export function getRoomProgress(roomId) {
  return apiGet(
    `/progress/rooms/${roomId}`,
  )
}

export function getModuleProgress(moduleId) {
  return apiGet(
    `/progress/modules/${moduleId}`,
  )
}

export function getLearningPathProgress(
  learningPathId,
) {
  return apiGet(
    `/progress/learning-paths/${learningPathId}`,
  )
}

export function completeLesson(lessonId) {
  return apiPost(
    `/progress/lessons/${lessonId}/complete`,
  )
}

export function completeRoom(roomId) {
  return apiPost(
    `/progress/rooms/${roomId}/complete`,
  )
}

export function completeModule(moduleId) {
  return apiPost(
    `/progress/modules/${moduleId}/complete`,
  )
}

export function completeLearningPath(
  learningPathId,
) {
  return apiPost(
    `/progress/learning-paths/${learningPathId}/complete`,
  )
}

export function listCompletedRooms(moduleId) {
  const query = moduleId
    ? `?module_id=${encodeURIComponent(moduleId)}`
    : ''

  return apiGet(
    `/progress/completed/rooms${query}`,
  )
}

export function listCompletedModules(
  learningPathId,
) {
  const query = learningPathId
    ? `?learning_path_id=${encodeURIComponent(
        learningPathId,
      )}`
    : ''

  return apiGet(
    `/progress/completed/modules${query}`,
  )
}

export function getLessonCompletionState(
  lessonId,
) {
  return apiGet(
    `/progress/lessons/${lessonId}/completion-state`,
  )
}
