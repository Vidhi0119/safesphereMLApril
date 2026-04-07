import { API_ENDPOINTS } from '../config/api';

/**
 * Get safety prediction for a given location
 * @param {number} latitude - Latitude coordinate
 * @param {number} longitude - Longitude coordinate
 * @returns {Promise<Object>} Safety prediction data
 */
export const getSafetyPrediction = async (latitude, longitude) => {
  try {
    const response = await fetch(API_ENDPOINTS.PREDICT_SAFETY, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        latitude,
        longitude,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching safety prediction:', error);
    throw error;
  }
};

/**
 * Check API health status
 * @returns {Promise<Object>} API health status
 */
export const checkApiHealth = async () => {
  try {
    const response = await fetch(API_ENDPOINTS.HEALTH);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error checking API health:', error);
    throw error;
  }
};

