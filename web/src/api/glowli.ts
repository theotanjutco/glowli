import axios from 'axios';
import { API_BASE_URL } from '../config/api';
import type { AnalyzeResponse } from '../types/analysis';

type ApiErrorBody = {
  detail?: string;
};

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
});

export async function analyzeSelfie(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<AnalyzeResponse>('/analyze', formData);
  return response.data;
}

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError<ApiErrorBody>(error)) {
    if (!error.response) {
      return 'Could not reach Glowli. Check that FastAPI is running and the API URL is correct.';
    }

    return error.response.data?.detail ?? 'Glowli could not analyze this image.';
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'An unexpected error occurred while analyzing the selfie.';
}

export default api;

