from io import BytesIO #file like object in memory that stores binary data
import warnings
from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError  # Provides image decoding, rotation, and validation.

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MIN_IMAGE_WIDTH = 400
MIN_IMAGE_HEIGHT = 400  
MAX_TOTAL_PIXELS = 20_000_000  # 20 million pixels, prevents large images

ALLOWED_CONTENT_TYPES = { "image/jpeg", "image/png", "image/webp" } #Lists accepted browser MIME types
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP", "MPO"}

async def validate_uploaded_image(file: UploadFile) -> Image.Image:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException( status_code = 415, detail = "Unsupported image type. Please upload a JPEG, PNG, or WebP image." )

    contents = await file.read(MAX_FILE_SIZE_BYTES + 1)

    # moving the read cursor to the start
    #resets the uploaded file in case another service needs
    await file.seek(0)

    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.",)

    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="Image must be 10 MB or smaller.",)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning) #Treats suspicious dimensions as an error

            with Image.open(BytesIO(contents)) as uploaded_image: # Opens the bytes without writing them to disk.
                detected_format = uploaded_image.format # Records the real format found inside the file.
                uploaded_image.verify()
    
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning): #Handles invalid or dangerous images
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid image.")

    if detected_format not in ALLOWED_IMAGE_FORMATS:
        raise HTTPException(status_code=415, detail="The image contents must be JPEG, PNG, or WebP.")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)

            with Image.open(BytesIO(contents)) as uploaded_image:  
                uploaded_image.seek(0)
                width, height = uploaded_image.size

                if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
                    raise HTTPException(
                        status_code=400,
                        detail="Image must be at least 400 by 400 pixels",
                    )

                if width * height > MAX_TOTAL_PIXELS:
                    raise HTTPException(
                        status_code=413,
                        detail="Image dimensions are too large.",
                    )

                rotated_image = ImageOps.exif_transpose(uploaded_image)
                normalized_image = rotated_image.convert("RGB")

                clean_image = normalized_image.copy()
                clean_image.info.clear() #Removes metadata carried over from original

    except HTTPException:
        raise

    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise HTTPException(status_code=400, detail="Glowli could not proccess this image.",)

    return clean_image
