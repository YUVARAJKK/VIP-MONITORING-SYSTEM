from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from threat_detection import ThreatDetectionEngine

app = FastAPI()

# Allow all origins for development (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = ThreatDetectionEngine()

@app.on_event("startup")
async def startup_event():
    await engine.initialize()

@app.get("/status")
async def get_status():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_post(request: Request):
    data = await request.json()
    result = await engine.analyze_post(
        content=data.get("content", ""),
        author=data.get("author", ""),
        platform=data.get("platform", ""),
        post_url=data.get("post_url", ""),
        image_urls=data.get("image_urls", []),
    )
    return result