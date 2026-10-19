import { fireEvent, render, screen } from '@testing-library/react';
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
            summary: 'Found 1 possible acne region. Results are experimental.',
            image_width: 400,
            image_height: 400,
            detections: [
                {
                    label: "Acne",
                    confidence: 0.7,
                    box: { x1: 0.1, y1: 0.2, x2: 0.3, y2: 0.4 },
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
        expect(screen.getByText(/model confidence 70%/i)).toBeInTheDocument();

        const photo = screen.getByRole('img', { name: 'Uploaded selfie' });
        Object.defineProperty(photo, 'naturalWidth', { configurable: true, value: 400 });
        Object.defineProperty(photo, 'naturalHeight', { configurable: true, value: 400 });
        fireEvent.load(photo);

        const box = screen.getByTestId('detection-box');
        expect(box).toHaveStyle({ left: '10%', top: '20%' });
        expect(parseFloat(box.style.width)).toBeCloseTo(20);
        expect(parseFloat(box.style.height)).toBeCloseTo(20);

        Object.defineProperty(photo, 'naturalWidth', { configurable: true, value: 800 });
        fireEvent.load(photo);
        expect(screen.queryByTestId('detection-box')).not.toBeInTheDocument();
        expect(screen.getByRole('alert')).toHaveTextContent(/dimensions differ/i);
    });
});
