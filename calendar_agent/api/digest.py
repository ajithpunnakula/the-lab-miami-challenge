from fastapi import APIRouter, HTTPException
from datetime import datetime
import os
from calendar_agent.utils.event_service import EventService
from calendar_agent.utils.textbelt_sms import TextBeltSMSClient

router = APIRouter()

@router.post("/digest")
async def send_weekly_digest():
    try:
        event_service = EventService()
        sms_client = TextBeltSMSClient(
            api_key=os.getenv("TEXTBELT_API_KEY"),
            to_number=os.getenv("SMS_TO_NUMBER", "2098129451")
        )
        
        upcoming_events = await event_service.get_upcoming_events()
        
        if not upcoming_events:
            return {
                "status": "no_events",
                "message": "No upcoming events to include in digest",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        result = await sms_client.send_weekly_digest(upcoming_events)
        
        if result["success"]:
            return {
                "status": "success",
                "events_included": len(upcoming_events),
                "message_id": result.get("message_id"),
                "ai_generated": result.get("ai_generated", False),
                "tokens_used": result.get("tokens_used", 0),
                "service": result.get("service", "TextBelt"),
                "quota_remaining": result.get("quota_remaining"),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "failed",
                "error": result.get("error"),
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await sms_client.close()