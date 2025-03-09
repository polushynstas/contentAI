// Базовий URL для API
export const API_BASE_URL = 'http://localhost:5001';

// Ендпоінти API
export const API_ENDPOINTS = {
  SIGNUP: `${API_BASE_URL}/signup`,
  LOGIN: `${API_BASE_URL}/login`,
  GENERATE: `${API_BASE_URL}/generate`,
  CHECK_SUBSCRIPTION: `${API_BASE_URL}/check-subscription`,
  UPDATE_SUBSCRIPTION: `${API_BASE_URL}/update-subscription`,
  USER_INFO: `${API_BASE_URL}/user-info`,
  PROFILE: `${API_BASE_URL}/user-info`,
  TRENDS: `${API_BASE_URL}/trends`,
  HEALTH: `${API_BASE_URL}/health`,
  TEST_OPENAI: `${API_BASE_URL}/test-openai`
}; 