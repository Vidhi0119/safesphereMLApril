// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/`,
  PREDICT_SAFETY: `${API_BASE_URL}/predict-safety`,
};

export default API_BASE_URL;

