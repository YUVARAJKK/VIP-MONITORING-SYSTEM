from fastapi import FastAPI, APIRouter, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import asyncio
from threat_detection import ThreatDetectionEngine
from social_monitor import SocialMediaMonitor

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize threat detection and monitoring
threat_engine = ThreatDetectionEngine()
social_monitor = SocialMediaMonitor(threat_engine, db)

# Create the main app without a prefix
app = FastAPI(title="VIP Threat Monitoring System")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class ThreatAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str
    author: str
    content: str
    url: str
    platform: str  # "Twitter", "Facebook", "Instagram"
    reason: str
    score: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ai_analysis: Optional[str] = None
    threat_level: str = "medium"  # low, medium, high, critical

class MonitoringStatus(BaseModel):
    is_running: bool
    platforms_monitored: List[str]
    alerts_count: int
    last_check: datetime

# Global monitoring task
monitoring_task = None

@api_router.get("/")
async def root():
    return {"message": "VIP Threat Monitoring System API"}

@api_router.get("/alerts", response_model=List[ThreatAlert])
async def get_alerts():
    """Get all threat alerts from the database"""
    alerts = await db.threat_alerts.find().sort("timestamp", -1).limit(100).to_list(100)
    return [ThreatAlert(**alert) for alert in alerts]

@api_router.get("/alerts/recent", response_model=List[ThreatAlert])
async def get_recent_alerts():
    """Get alerts from the last 24 hours"""
    from datetime import timedelta
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
    alerts = await db.threat_alerts.find(
        {"timestamp": {"$gte": cutoff_time}}
    ).sort("timestamp", -1).to_list(50)
    return [ThreatAlert(**alert) for alert in alerts]

@api_router.get("/status", response_model=MonitoringStatus)
async def get_monitoring_status():
    """Get current monitoring status"""
    global monitoring_task
    is_running = monitoring_task is not None and not monitoring_task.done()
    
    alerts_count = await db.threat_alerts.count_documents({})
    last_check = datetime.now(timezone.utc)
    
    return MonitoringStatus(
        is_running=is_running,
        platforms_monitored=["Twitter", "Facebook", "Instagram"],
        alerts_count=alerts_count,
        last_check=last_check
    )

@api_router.post("/monitoring/start")
async def start_monitoring(background_tasks: BackgroundTasks):
    """Start the social media monitoring"""
    global monitoring_task
    
    if monitoring_task is None or monitoring_task.done():
        monitoring_task = asyncio.create_task(social_monitor.start_monitoring())
        return {"message": "Monitoring started successfully"}
    else:
        return {"message": "Monitoring is already running"}

@api_router.post("/monitoring/stop")
async def stop_monitoring():
    """Stop the social media monitoring"""
    global monitoring_task
    
    if monitoring_task and not monitoring_task.done():
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass
        return {"message": "Monitoring stopped successfully"}
    else:
        return {"message": "Monitoring is not running"}

@api_router.delete("/alerts")
async def clear_alerts():
    """Clear all alerts from the database"""
    result = await db.threat_alerts.delete_many({})
    return {"message": f"Cleared {result.deleted_count} alerts"}

@api_router.get("/test/generate-mock-alert")
async def generate_mock_alert():
    """Generate a mock alert for testing"""
    mock_alert = ThreatAlert(
        post_id="mock_" + str(uuid.uuid4())[:8],
        author="test_user_123",
        content="This is a mock threatening message for testing purposes",
        url="https://twitter.com/test_user_123/status/123456789",
        platform="Twitter",
        reason="Violence & Threat Detection",
        score=0.85,
        ai_analysis="This message contains threatening language and violent intent",
        threat_level="high"
    )
    
    await db.threat_alerts.insert_one(mock_alert.dict())
    return {"message": "Mock alert generated", "alert": mock_alert}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("VIP Threat Monitoring System starting up...")
    await threat_engine.initialize()
    logger.info("Threat detection engine initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global monitoring_task
    
    if monitoring_task and not monitoring_task.done():
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass
    
    client.close()
    logger.info("VIP Threat Monitoring System shutting down...")