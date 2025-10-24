from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from utils.event_service import EventService
from utils.reminder_tracker import ReminderTracker

router = APIRouter()

@router.get("/stats")
async def get_stats():
    try:
        event_service = EventService()
        reminder_tracker = ReminderTracker()
        
        stats = await event_service.get_event_stats()
        
        reminders_sent_count = reminder_tracker.get_reminders_sent_count()
        
        return {
            "status": "success",
            "statistics": {
                "total_events": stats["total_events"],
                "upcoming_events": stats["upcoming_events"],
                "past_events": stats["past_events"],
                "reminders_sent_total": reminders_sent_count,
                "data_source": "Luma (live)"
            },
            "next_event": stats["next_event"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))