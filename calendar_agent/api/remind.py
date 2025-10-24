from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import os
from calendar_agent.utils.event_service import EventService
from calendar_agent.utils.reminder_tracker import ReminderTracker
from calendar_agent.utils.textbelt_sms import TextBeltSMSClient

router = APIRouter()

REMINDER_WINDOWS = [
    (timedelta(hours=24), "24_hours"),
    (timedelta(hours=2), "2_hours"),
    (timedelta(minutes=30), "30_minutes")
]

@router.post("/remind")
async def send_reminders():
    try:
        event_service = EventService()
        reminder_tracker = ReminderTracker()
        sms_client = TextBeltSMSClient(
            api_key=os.getenv("TEXTBELT_API_KEY"),
            to_number=os.getenv("SMS_TO_NUMBER", "+12098128451")
        )
        
        reminders_sent = []
        
        # Get events that need reminders
        events_needing_reminders = await event_service.get_events_needing_reminders(REMINDER_WINDOWS)
        
        for event in events_needing_reminders:
            reminder_key = event["reminder_key"]
            
            if not reminder_tracker.is_reminder_sent(reminder_key):
                result = await sms_client.send_ai_reminder(event, event["reminder_type"])
                
                if result["success"]:
                    reminder_tracker.mark_reminder_sent(reminder_key)
                    reminders_sent.append({
                        "event_id": event["id"],
                        "event_title": event["title"],
                        "reminder_type": event["reminder_type"],
                        "message_id": result.get("message_id"),
                        "ai_generated": result.get("ai_generated", False),
                        "tokens_used": result.get("tokens_used", 0),
                        "service": result.get("service", "TextBelt"),
                        "quota_remaining": result.get("quota_remaining")
                    })
        
        return {
            "status": "success",
            "reminders_sent": len(reminders_sent),
            "details": reminders_sent,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await sms_client.close()

@router.post("/updates")
async def send_live_updates():
    """Send live updates about today's events (for 5-minute intervals)"""
    try:
        event_service = EventService()
        reminder_tracker = ReminderTracker()
        sms_client = TextBeltSMSClient(
            api_key=os.getenv("TEXTBELT_API_KEY"),
            to_number=os.getenv("SMS_TO_NUMBER", "+12098128451")
        )
        
        # Get today's events
        upcoming_events = await event_service.get_upcoming_events()
        now = datetime.utcnow()
        today = now.date()
        
        today_events = []
        for event in upcoming_events:
            try:
                event_time = datetime.fromisoformat(event['start_time'])
                if event_time.date() == today:
                    today_events.append(event)
            except (ValueError, KeyError):
                continue
        
        # Create update key for this 5-minute interval
        interval_key = f"update_{now.strftime('%Y%m%d_%H%M')}"
        
        if not reminder_tracker.is_reminder_sent(interval_key) and today_events:
            # Create update message
            if len(today_events) == 1:
                event = today_events[0]
                event_time = datetime.fromisoformat(event['start_time'])
                time_until = event_time - now
                hours = int(time_until.total_seconds() // 3600)
                minutes = int((time_until.total_seconds() % 3600) // 60)
                
                if hours > 0:
                    time_str = f"{hours}h {minutes}m"
                else:
                    time_str = f"{minutes}m"
                
                message = f"🕒 Today's Event: {event['title']}\n⏰ Starting in {time_str}\n🔗 {event['link']}"
            else:
                message = f"📅 Today: {len(today_events)} events happening!\n"
                for i, event in enumerate(today_events[:3], 1):
                    event_time = datetime.fromisoformat(event['start_time'])
                    message += f"{i}. {event['title']} at {event_time.strftime('%I:%M %p')}\n"
                if len(today_events) > 3:
                    message += f"...and {len(today_events) - 3} more!"
            
            result = await sms_client.send_sms(message)
            
            if result["success"]:
                reminder_tracker.mark_reminder_sent(interval_key)
                return {
                    "status": "success",
                    "update_sent": True,
                    "events_today": len(today_events),
                    "message_id": result.get("message_id"),
                    "quota_remaining": result.get("quota_remaining"),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        return {
            "status": "success",
            "update_sent": False,
            "events_today": len(today_events),
            "reason": "No events today or update already sent for this interval",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await sms_client.close()
@router.post("/demo")
async def send_demo_sms():
    """Demo endpoint: Send SMS with next planned event regardless of timing"""
    try:
        event_service = EventService()
        sms_client = TextBeltSMSClient(
            api_key=os.getenv("TEXTBELT_API_KEY"),
            to_number=os.getenv("SMS_TO_NUMBER", "+12098128451")
        )
        
        # Get all upcoming events
        upcoming_events = await event_service.get_upcoming_events()
        
        if not upcoming_events:
            # Send a message saying no events found
            message = "🤖 Demo SMS from Calendar Agent!\\n\\n📅 No upcoming events found on The Lab Miami calendar.\\n\\n✅ SMS integration working!"
            result = await sms_client.send_sms(message)
        else:
            # Send info about the next event
            next_event = upcoming_events[0]
            event_time = datetime.fromisoformat(next_event["start_time"])
            formatted_time = event_time.strftime("%m/%d at %I:%M %p")
            
            message = f"🤖 Demo: Next Lab Event!\\n\\n📅 {next_event['title']}\\n⏰ {formatted_time}\\n🔗 {next_event['link']}\\n\\n✅ SMS working!"
            result = await sms_client.send_sms(message)
        
        if result["success"]:
            return {
                "status": "demo_success",
                "message_sent": True,
                "events_found": len(upcoming_events),
                "message_id": result.get("message_id"),
                "quota_remaining": result.get("quota_remaining"),
                "service": result.get("service", "TextBelt"),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "demo_failed",
                "message_sent": False,
                "error": result.get("error"),
                "events_found": len(upcoming_events),
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await sms_client.close()
