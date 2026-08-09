import axios from 'axios'; //Axios is a JS library for making HTTP requests
import { API_BASE_URL } from '../config/api';
import type { AnalyzeResponse } from '../types/analysis';

type APIErrorBody = {
    detail?: string;
};

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout:30000,
});

// Send the selected selfie to FastAPI as multipart/form-data
 export async function analyzeSelfie(uri: string,): Promise<AnalyzeResponse> {
    // Create a multipart form body capable of containing a file
    const formData = new FormData();

    const imageFile = {
        uri,
        name:'glowli-selfie.jpg',
        type:'image/jpeg',
    } as unknown as Blob;

    formData.append('file', imageFile);

    const response = await api.post<AnalyzeResponse>('/analyze', formData);

return response.data;
}

// Convert an unknown caught error into a message suitable for the user 
export function getAPIErrorMessage(error: unknown): string {
    if (axios.isAxiosError<APIErrorBody>(error)) {
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