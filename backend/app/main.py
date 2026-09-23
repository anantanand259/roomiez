from fastapi import FastAPI
from app.api import rooms, auth

app = FastAPI(
    title="Roomiez API",
    description="Student Accommodation Discovery & Verification Platform",
    version="1.0.0"
)

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(rooms.router, prefix="/api/v1", tags=["rooms"])

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "message": "Roomiez API is running"}