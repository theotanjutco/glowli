const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024;

const ALLOWED_IMAGE_TYPES = new Set([
    'image/jpeg',
    'image/png',
    'image/webp',
])

export function getImageValidationError(file: File): string | null {
    if (!ALLOWED_IMAGE_TYPES.has(file.type)) {
        return 'Upload a JPEG, PNG, or WebP image.';
    }

    if (file.size === 0) {
        return 'The selected image is empty.';
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
        return 'Image must be 10 MB or smaller.'
    }

    return null;
}