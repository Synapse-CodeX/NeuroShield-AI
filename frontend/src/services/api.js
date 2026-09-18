const BASE_URL = ''; // Uses Vite proxy

/**
 * Convert API/network failures into short, user-facing errors.
 * Raw backend traces, HTML responses, and provider errors should never
 * leak into the UI.
 */
const getErrorMessage = async (response) => {
  let payload = null;

  try {
    payload = await response.json();
  } catch {
    // Response wasn't JSON.
  }

  if (payload?.detail) {
    const detail =
      typeof payload.detail === 'string'
        ? payload.detail
        : 'The server returned an invalid error response.';

    const normalized = detail.toLowerCase();

    if (
      response.status === 429 ||
      normalized.includes('resource_exhausted') ||
      normalized.includes('rate limit') ||
      normalized.includes('quota')
    ) {
      return 'The AI service is temporarily rate-limited. Please try again later.';
    }

    if (
      normalized.includes('timeout') ||
      normalized.includes('timed out')
    ) {
      return 'The request took too long to complete. Please try again.';
    }

    if (
      normalized.includes('connection') ||
      normalized.includes('connect')
    ) {
      return 'The analysis service could not be reached. Please try again.';
    }

    return detail;
  }

  if (response.status === 400) {
    return 'Please check your input and try again.';
  }

  if (response.status === 404) {
    return 'The requested analysis session was not found. Please run the analysis again.';
  }

  if (response.status === 429) {
    return 'The AI service is temporarily rate-limited. Please try again later.';
  }

  if (response.status >= 500) {
    return 'The NeuroShield analysis service encountered an error. Please try again.';
  }

  return `Request failed (${response.status}). Please try again.`;
};

/**
 * Execute a JSON API request with consistent error handling.
 */
const request = async (path, options = {}) => {
  let response;

  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    });
  } catch {
    throw new Error(
      'Unable to reach the NeuroShield server. Make sure the backend is running and try again.'
    );
  }

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  try {
    return await response.json();
  } catch {
    throw new Error('The server returned an invalid response. Please try again.');
  }
};


// ============================================================
// PRIVACY
// ============================================================

export const analyzePrivacy = async (text) => {
  return request('/api/privacy/analyze', {
    method: 'POST',
    body: JSON.stringify({
      raw_text: text,
    }),
  });
};

export const chatPrivacy = async (question, sessionId) => {
  return request('/api/privacy/chat', {
    method: 'POST',
    body: JSON.stringify({
      question,
      session_id: sessionId,
    }),
  });
};


// ============================================================
// FACT CHECKER
// ============================================================

export const checkFacts = async (text) => {
  return request('/api/factcheck/analyze', {
    method: 'POST',
    body: JSON.stringify({
      input_text: text,
    }),
  });
};


// ============================================================
// WEBSITE SCANNER
// ============================================================

export const scanWebsite = async (url) => {
  return request('/api/scanner/scan', {
    method: 'POST',
    body: JSON.stringify({
      url,
    }),
  });
};

export const chatScanner = async (question, sessionId) => {
  return request('/api/scanner/chat', {
    method: 'POST',
    body: JSON.stringify({
      question,
      session_id: sessionId,
    }),
  });
};