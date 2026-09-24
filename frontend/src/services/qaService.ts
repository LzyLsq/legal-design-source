import { QARequest, QAResponse } from '../types/qa';

const url = 'http://localhost:8012/v1/chat/completions';
const headers = { 'Content-Type': 'application/json' };

export const askQuestion = async (request: QARequest): Promise<QAResponse> => {
  const response = await fetch(url, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error('Failed to get answer');
  }

  return response.json();
};