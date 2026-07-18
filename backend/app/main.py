from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, Annotated

#------Create FastAPI app--------------
app = FastAPI(
    title = "Glowli API",
    description = "AI-powered facial skin analysis and skincare recommendation API",
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

#-----The blueprint/exact JSON shape the web app will receive---------
# helps frontend and backend agree before using YOLO (pydantic)
class SkinCondition(BaseModel):
    label: str
    severity: Literal["mild", "moderate", "severe"]
    confidence: float
    description: str

class AnalyzeResponse(BaseModel):
    skin_type: Literal["oily", "dry", "combination", "sensitive", "normal"]
    summary: str
    conditions: list[SkinCondition]

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
# Returns mock info as of now
@app.post("/analyze", response_model = AnalyzeResponse)
async def analyze_skin(file: Annotated[UploadFile, File()]):
    contents = await file.read()

    if not contents:
        raise HTTPException(status_code = 400, detail = "Uploaded image is empty")
    
    # mock response for now
    return AnalyzeResponse(
        skin_type = "combination",
        summary = "Mock scan complete. Glowli found a few mild areas to review.",
        conditions = [
            SkinCondition(
                label = "Acne",
                severity = "mild",
                confidence = .93,
                description = "A small number of blemish-like spots were detected.",
            )
        ],
    )
    
