// Import Analysis type because its not needed in runtime
import type { AnalyzeResponse } from './analysis';

// Define every screen name and expected parameters for that screeen
export type RootStackParamList = {
    Home: undefined;
    Camera: undefined;
    Results: { analysis: AnalyzeResponse };
}; 