import cv2

from fastapi import FastAPI, File, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, Annotated

from app.image_validation import validate_uploaded_image
from app.face_detection import count_faces
from app.acne_detection import predict_acne

#------Create FastAPI app--------------
app = FastAPI(
    title = "Glowli API",
    description = "Experimental acne detection API",
    version = "0.1.0"
)

#-----CORS Middleware--------------
# Allows the local Glowli web app to talk to this backend during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"], # Allow all HTTP methods
    allow_headers=["*"],
)

class BoundingBox(BaseModel):
    x1: float = Field(ge=0, le=1)
    y1: float = Field(ge=0, le=1)
    x2: float = Field(ge=0, le=1)
    y2: float = Field(ge=0, le=1)


class AcneDetection(BaseModel):
    label: Literal["Acne"]
    confidence: float = Field(ge=0, le=1)
    box: BoundingBox


class AnalyzeResponse(BaseModel):
    summary: str
    image_width: int = Field(gt=0)
    image_height: int = Field(gt=0)
    detections: list[AcneDetection]

#------Routes-------------------------
@app.get("/")
def root():
    return {"message": "Welcome to Glowli App"}

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": "Glowli API",
        "version": "0.1.0"
    }

# Selfie Scan endpoint
@app.post("/analyze", response_model = AnalyzeResponse)
async def analyze_skin(file: Annotated[UploadFile, File()]) -> AnalyzeResponse:
    validated_image = await validate_uploaded_image(file)

    try:
        face_count = await run_in_threadpool(count_faces, validated_image)
    except (RuntimeError, cv2.error) as exc:
        raise HTTPException(
            status_code=503,
            detail="Face detection is currently unavailable. Please try again later.",
        ) from exc

    if face_count == 0:
        raise HTTPException(
            status_code=400,
            detail="No face detected. Please upload a clear, front-facing selfie.",
        )

    if face_count > 1:
        raise HTTPException(
            status_code=400,
            detail="Multiple faces detected. Please upload a photo of only yourself.",
        )
    try:
        predictions = await run_in_threadpool(predict_acne, validated_image)
    except (RuntimeError, OSError, cv2.error) as exc:
        raise HTTPException(
            status_code=503,
            detail="Acne detection is currently unavailable. Please try again later.",
        ) from exc

    detections = [
        AcneDetection.model_validate(prediction)
        for prediction in predictions
    ]
    summary = (
        f"Found {len(detections)} possible acne regions. Results are experimental."
        if detections
        else "No detections above the confidence threshold. This does not rule out acne."
    )

    return AnalyzeResponse(
        summary=summary,
        image_width=validated_image.width,
        image_height=validated_image.height,
        detections=detections,
    )
