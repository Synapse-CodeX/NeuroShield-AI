const BASE_URL = ''; // Uses Vite proxy

export const analyzePrivacy = async (text) => {
  const res = await fetch(`${BASE_URL}/api/privacy/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw_text: text })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
};

export const chatPrivacy = async (question, sessionId) => {
  const res = await fetch(`${BASE_URL}/api/privacy/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, session_id: sessionId })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
};

export const checkFacts = async (text) => {
  const res = await fetch(`${BASE_URL}/api/factcheck/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ input_text: text })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
};

export const scanWebsite = async (url) => {
  const res = await fetch(`${BASE_URL}/api/scanner/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
};

export const chatScanner = async (question, sessionId) => {
  const res = await fetch(`${BASE_URL}/api/scanner/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, session_id: sessionId })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
};
