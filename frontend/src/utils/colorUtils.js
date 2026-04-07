/**
 * Get color based on safety score (1-10)
 * Uses red shades: darker red for low scores, lighter red for high scores
 * @param {number} safetyScore - Safety score from 1 to 10
 * @returns {string} Hex color code
 */
export const getSafetyColor = (safetyScore) => {
  // Clamp score between 1 and 10
  const score = Math.max(1, Math.min(10, safetyScore));
  
  // Normalize to 0-1 range (inverted: 1 = darkest red, 10 = lightest red)
  const normalized = (11 - score) / 10;
  
  // Red color gradient: from dark red (#8B0000) to light red (#FFE5E5)
  // Dark red: RGB(139, 0, 0) - Low safety
  // Light red: RGB(255, 229, 229) - High safety
  
  const r = Math.round(139 + (255 - 139) * (1 - normalized));
  const g = Math.round(0 + (229 - 0) * (1 - normalized));
  const b = Math.round(0 + (229 - 0) * (1 - normalized));
  
  return `rgb(${r}, ${g}, ${b})`;
};

/**
 * Get background color for safety score display
 * @param {number} safetyScore - Safety score from 1 to 10
 * @returns {string} Tailwind CSS class or hex color
 */
export const getSafetyBgColor = (safetyScore) => {
  const score = Math.max(1, Math.min(10, safetyScore));
  
  if (score >= 8) return 'bg-red-100'; // Light red
  if (score >= 6) return 'bg-red-200'; // Medium-light red
  if (score >= 4) return 'bg-red-300'; // Medium red
  if (score >= 2) return 'bg-red-400'; // Medium-dark red
  return 'bg-red-500'; // Dark red
};

/**
 * Get text color for safety score display
 * @param {number} safetyScore - Safety score from 1 to 10
 * @returns {string} Tailwind CSS class
 */
export const getSafetyTextColor = (safetyScore) => {
  const score = Math.max(1, Math.min(10, safetyScore));
  
  if (score >= 6) return 'text-red-800'; // Dark text for light backgrounds
  return 'text-white'; // White text for dark backgrounds
};

