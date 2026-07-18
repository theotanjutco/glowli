import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Import Vitest's test, assertion, and mocking functions.
import { describe, expect, it, vi } from 'vitest';

import App from './App';
import { analyzeSelfie } from './api/glowli';   

vi.mock('./api/glowli', () => ({
    // Create a mock for the selfie upload request
    analyzeSelfie:vi.fn(),

    getApiErrorMessage: vi.fn(() => 'Analysis failed.'),
}))

// Group tests that describe the complete browser workflow
describe('Glowli browser workflow', () => {
    it('uploads a selfie and displays the returned results', async () => {
        // Create a user controller for realistic clicking and uploading
        const user = userEvent.setup();

        // Configure the mocked API to return the same shape as FastAPI
        vi.mocked(analyzeSelfie).mockResolvedValue({
            skin_type: "combination",
            summary: "Test Scan complete",
            conditions: [
                {
                    label: "Acne",
                    severity: 'mild',
                    confidence: 0.93,
                    description: 'A test condition description.',
                }
            ]
        });
        
        // Render Glowli App at Home Page
        render(<App />);

        await user.click(screen.getByRole('button', {name: /analyze a selfie/i }))

        // Construct a browser File object representing the selected selfie.
        const selfie = new File(['image-content'], 'selfie.jpg', {
            // Mark the file with the MIME type expected by the upload control.
            type: 'image/jpeg',
        });

        await user.upload(screen.getByLabelText(/selfie upload form/i).querySelector('input')!, selfie);
        await user.click(screen.getByRole('button', { name: /analyze selfie/i}));

        // Confirm that the API received the exact File selected by the user
        expect(analyzeSelfie).toHaveBeenCalledWith(selfie);
        expect(await screen.findByText('Your Glowli results')).toBeInTheDocument();
        expect(screen.getByText('Acne')).toBeInTheDocument();
        expect(screen.getByText('93%')).toBeInTheDocument();
    });
});
