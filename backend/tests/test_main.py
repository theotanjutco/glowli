from io import BytesIO

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

def test_analyze_accepts_valid_image() -> None:
    image_bytes = create_test_image()

    files = {
        "file": (
            "selfie.jpg",
            image_bytes,
            "image/jpeg",
        )
    }

    response = client.post("/analyze", files=files) #uploade image to glowli

    assert response.status_code == 200 # confirms that validation succeeded

    body = response.json() #converts json response to python dict

    assert body["skin_type"] == "combination"  # Confirms the current mocked skin type.
    assert len(body["conditions"]) > 0  # Confirms that at least one condition was returned.
    assert body["conditions"][0]["label"] == "Acne"  # Confirms the mocked condition.
    assert body["conditions"][0]["confidence"] == 0.93  # Confirms the mocked confidence.

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