import { ComplianceResponse } from '../types/compliance';

export const checkCompliance = async (file: File, provider: string): Promise<ComplianceResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`http://localhost:8000/compliance/${provider}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Failed to check compliance');
  }

  return response.json();
};
