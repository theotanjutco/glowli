from io import BytesIO
from unittest.mock import patch

import cv2
import pytest

# Import FastAPI's synchronous test client
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

# Create the test client 
client = TestClient(app)

def create_test_image(width: int = 400, height: int = 400, image_format: str = "JPEG") -> bytes:
    image_buffer = BytesIO() # Creates an empty in-memory binary file
    image = Image.new("RGB", (width, height), color="white")
    image.save(image_buffer, format = image_format)
    return image_buffer.getvalue() #returns the encoded image as bytes


def test_health_check_returns_ok() -> None:
    response = client.get("/health")

    # assert tests if condition is true
    assert response.status_code == 200

    assert response.json() == {
        "status":"ok",
        "app":"Glowli API",
        "version":"0.1.0",
    }

@pytest.mark.parametrize(
    "predictions",
    [
        [],
        [{
            "label": "Acne",
            "confidence": 0.7,
            "box": {"x1": 0.1, "y1": 0.2, "x2": 0.3, "y2": 0.4},
        }],
    ],
)
def test_analyze_accepts_valid_image(predictions: list[dict]) -> None:
    files = {"file": ("selfie.jpg", create_test_image(), "image/jpeg")}

    with (
        patch("app.main.count_faces", return_value=1) as face_detector,
        patch("app.main.predict_acne", return_value=predictions) as acne_detector,
    ):
        response = client.post("/analyze", files=files)

    face_detector.assert_called_once()
    acne_detector.assert_called_once()
    assert response.status_code == 200

    body = response.json()
    assert body["detections"] == predictions
    assert body["image_width"] == 400
    assert body["image_height"] == 400
    assert "skin_type" not in body
    assert "conditions" not in body
    if not predictions:
        assert "does not rule out acne" in body["summary"]


@pytest.mark.parametrize(
    "failure",
    [
        RuntimeError("Model unavailable"),
        OSError("Cannot read model"),
        cv2.error("Inference failed"),
    ],
)
def test_analyze_handles_acne_failure(failure: Exception) -> None:
    files = {"file": ("selfie.jpg", create_test_image(), "image/jpeg")}

    with (
        patch("app.main.count_faces", return_value=1),
        patch("app.main.predict_acne", side_effect=failure),
    ):
        response = client.post("/analyze", files=files)

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Acne detection is currently unavailable. Please try again later."
    )

def test_analyze_rejects_empty_upload() -> None:
    files = {"file": ("empty.jpg", b"", "image/jpeg")}

    response = client.post("/analyze", files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded image is empty."

def test_analyze_rejects_unsupported_content_type() -> None:
    files = {  # Creates multipart form data.
        "file": (  # Uses the required file field.
            "notes.txt",  # Gives the upload a text filename.
            b"This is not an image.",  # Provides plain-text contents.
            "text/plain",  # Identifies the upload as text.
        )
    }

    response = client.post("/analyze", files=files)

    assert response.status_code == 415
    assert response.json()["detail"] == (
        "Unsupported image type. Please upload a JPEG, PNG, or WebP image."
    )

def test_analyze_rejects_fake_image_bytes() -> None:
    files = {
        "file": (  # Uses the API's required file field.
            "fake.jpg",  # Gives the file a JPEG extension.
            b"these-are-not-real-image-bytes",  # Provides invalid image data.
            "image/jpeg",  # Falsely claims that the data is JPEG.
        )
    }

    response = client.post("/analyze", files=files)  # Uploads the fake image.

    assert response.status_code == 400  # Confirms that actual image decoding failed.
    assert response.json()["detail"] == (  # Checks the safe error message.
        "The uploaded file is not a valid image."
    )

def test_analyze_rejects_small_image() -> None:  # Tests an image below the minimum dimensions.
    image_bytes = create_test_image(width=200, height=200)  # Creates a small but valid JPEG.

    files = {  # Creates the multipart form data.
        "file": (  # Uses the required upload field.
            "small.jpg",  # Provides the image filename.
            image_bytes,  # Provides valid but undersized image bytes.
            "image/jpeg",  # Provides the correct MIME type.
        )
    }

    response = client.post("/analyze", files=files)  # Uploads the undersized image.

    assert response.status_code == 400  # Confirms that Glowli rejects small images.
    assert response.json()["detail"] == (  # Confirms the dimension error message.
        "Image must be at least 400 by 400 pixels"
    )


@pytest.mark.parametrize(
    ("face_count", "message"),
    [
        (
            0,
            "No face detected. Please upload a clear, front-facing selfie.",
        ),
        (
            2,
            "Multiple faces detected. Please upload a photo of only yourself.",
        ),
    ],
)
def test_analyze_rejects_invalid_face_count(
    face_count: int,
    message: str,
) -> None:
    files = {
        "file": ("selfie.jpg", create_test_image(), "image/jpeg"),
    }

    with patch("app.main.count_faces", return_value=face_count) as detector:
        response = client.post("/analyze", files=files)

    detector.assert_called_once()
    assert response.status_code == 400
    assert response.json()["detail"] == message


@pytest.mark.parametrize(
    "failure",
    [
        RuntimeError("The YuNet model file is missing."),
        cv2.error("Detection failed."),
    ],
)
def test_analyze_handles_detector_failure(failure: Exception) -> None:
    files = {
        "file": ("selfie.jpg", create_test_image(), "image/jpeg"),
    }

    with patch("app.main.count_faces", side_effect=failure):
        response = client.post("/analyze", files=files)

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Face detection is currently unavailable. Please try again later."
    )
