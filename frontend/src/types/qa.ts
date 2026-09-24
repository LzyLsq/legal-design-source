export interface QARequest {
  model: string;
  messages: Array<{ role: string; content: string }>;
  temperature: number;
}

export interface QAResponse {
  choices: Array<{ message: { content: string } }>;
}