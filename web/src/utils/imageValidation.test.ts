import { describe, expect, it } from 'vitest';
import { getImageValidationError } from './imageValidation';

describe('getImageValidationError', () => {
    it('accepts supported image types', () => {
        const jpegFile = new File(['image-data'], 'selfie.jpeg', {
            type: 'image/jpeg',
        });

        const pngFile = new File(['image-data'], 'selfie.png', {
            type: 'image/png',
        });

        const webpFile = new File(['image-data'], 'selfie.webp', {
            type: 'image/webp',
        });

        expect(getImageValidationError(jpegFile)).toBeNull();
        expect(getImageValidationError(pngFile)).toBeNull();
        expect(getImageValidationError(webpFile)).toBeNull();
    });

    it('rejects unsupported file types', () => {
        const textFile = new File(['not-an-image'], 'notes.txt', {
            type: 'text/plain',
        });

        const result = getImageValidationError(textFile);
        
        expect(result).toBe('Upload a JPEG, PNG, or WebP image.');
    });

    it('rejects empty image files', () => {
        const emptyFile = new File([], 'empty.jpg', {
            type: 'image/jpeg',
        });

        const result = getImageValidationError(emptyFile);

        expect(result).toBe('The selected image is empty.');
    });

    it('rejects images larger than 10 MB', () => {
        const oversizedBytes = new Uint8Array(10 * 1024 * 1024 + 1);

        const oversizedFile = new File([oversizedBytes], 'large.jpeg', {
            type: 'image/jpeg',
        });

        const result = getImageValidationError(oversizedFile);

        expect(result).toBe('Image must be 10 MB or smaller.');
    });
});