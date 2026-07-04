from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#------Create FastAPI app--------------
app = FastAPI(
    title = "Glowli API",
    description = "AI-powered facial skin analysis and skincare recommendation API",
    version = "0.1.0"
)

#-----CORS Middleware--------------
#allows app and web app to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow rerquests from everyone (change before shipping)
    allow_credentials=True,
    allow_methods=["*"], # Allow all HTTP methods
    allow_headers=["*"],
)

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