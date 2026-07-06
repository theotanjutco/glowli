import axios from 'axios'; //Axios is a JS library for making HTTP requests
import { API_BASE_URL } from '../config/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout:30000,
});

// Send the selected selfie to FastAPI as multipart/form-data
export async function analyzeSelfie(uri: string) {
    const formData = new FormData();

    formData.append('file', {
        uri,
        name: 'glowli-selfie.jpg',
        type: 'image/jpeg',
    } as any)

    const response = await api.post('analyze', formData, {
    headers: {'Content-Type': 'multipart/form-data'},
});

return response.data;

}

export default api; 