// Stores backendURL in one place
//For physical phone, replace localhoset with computers LAN IP
// To find run ipconfig and look for IPv4 address

// Read the public API URL that Expo loads from .env.local.
const configuredApiBaseUrl = process.env.EXPO_PUBLIC_API_URL;

if (!configuredApiBaseUrl) {
    throw new Error("EXPO_PUBLIC_API_URL is not defined in .env.local");
}

// Export the API base URL for use in other parts of the app
export const API_BASE_URL = configuredApiBaseUrl.replace(/\/$/, ''); // Remove trailing slash if present