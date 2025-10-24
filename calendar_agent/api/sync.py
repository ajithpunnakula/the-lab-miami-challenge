from fastapi import APIRouter, HTTPException
from datetime import datetime
import os
from utils.event_service import EventService

router = APIRouter()

@router.post("/sync")
async def sync_events():
    try:
        event_service = EventService()
        events = await event_service.fetch_all_events()
        
        return {
            "status": "success",
            "total_events": len(events),
            "events_fetched": len(events),
            "source": "Luma (live)",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))