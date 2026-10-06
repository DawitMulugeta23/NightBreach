import { apiGet, apiPost } from "./client.js";

export const startOnboarding = () => apiPost("/onboarding/start", {});

export const submitOnboardingAnswer = (questionId, optionIds, answerSheet) =>
  apiPost("/onboarding/answer", {
    question_id: questionId,
    option_ids: optionIds,
    answer_sheet: answerSheet,
  });

export const getOnboardingProfile = () => apiGet("/onboarding/profile");
