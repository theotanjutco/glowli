# Import FastAPI's synchronous test client
from fastapi.testclient import TestClient
from app.main import app

# Create the test client 
client = TestClient(app)

def test_health_check_returns_ok() -> None:
    response = client.get("/health")

    # assert tests if condition is true
    assert response.status_code == 200

    assert response.json() == {
        "status":"ok",
        "app":"Glowli API",
        "version":"0.1.0",
    }

def test_analyze_returns_typed_mock_result() -> None:

    # test input
    files = {"file":("selfie.jpg", b"temporary-image-bytes", "image/jpeg")}

    response = client.post("/analyze", files=files)

    assert response.status_code == 200
    body = response.json()

    # mock check
    assert body["skin_type"] == "combination"
    assert len(body["conditions"]) > 0
    assert body["conditions"][0]["label"] == "Acne"

def test_analyze_rejects_empty_upload() -> None:
    files = {"file": ("empty.jpg", b"", "image/jpeg")}

    response = client.post("/analyze", files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded image is empty"