import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from calendar_agent.utils.luma_scraper import LumaScraper

class EventService:
    """Service for fetching and filtering events directly from Luma"""
    
    def __init__(self):
        self.luma_url = os.getenv("LUMA_URL", "https://lu.ma/usr-vZ7w2FE5gUi7f1Y")
        self.scraper = LumaScraper(self.luma_url)
    
    async def fetch_all_events(self) -> List[Dict[str, Any]]:
        """Fetch all events from Luma"""
        return await self.scraper.fetch_events()
    
    async def get_upcoming_events(self) -> List[Dict[str, Any]]:
        """Get events that are in the future"""
        events = await self.fetch_all_events()
        now = datetime.utcnow()
        
        upcoming = []
        for event in events:
            try:
                event_time = datetime.fromisoformat(event['start_time'])
                if event_time > now:
                    upcoming.append(event)
            except (ValueError, KeyError):
                # Skip events with invalid dates
                continue
        
        # Sort by start time
        return sorted(upcoming, key=lambda x: x['start_time'])
    
    async def get_past_events(self) -> List[Dict[str, Any]]:
        """Get events that have already happened"""
        events = await self.fetch_all_events()
        now = datetime.utcnow()
        
        past = []
        for event in events:
            try:
                event_time = datetime.fromisoformat(event['start_time'])
                if event_time <= now:
                    past.append(event)
            except (ValueError, KeyError):
                # Skip events with invalid dates
                continue
        
        # Sort by start time (most recent first)
        return sorted(past, key=lambda x: x['start_time'], reverse=True)
    
    async def get_events_needing_reminders(self, reminder_windows: List[tuple]) -> List[Dict[str, Any]]:
        """Get events that need reminders based on the reminder windows"""
        upcoming_events = await self.get_upcoming_events()
        now = datetime.utcnow()
        
        events_needing_reminders = []
        
        for event in upcoming_events:
            try:
                event_time = datetime.fromisoformat(event['start_time'])
                
                for window, window_name in reminder_windows:
                    reminder_time = event_time - window
                    
                    # Check if we're in the reminder window (15-minute window)
                    if now >= reminder_time and now < reminder_time + timedelta(minutes=15):
                        event_copy = event.copy()
                        event_copy['reminder_type'] = window_name
                        event_copy['reminder_key'] = f"{event['id']}_{window_name}"
                        events_needing_reminders.append(event_copy)
                        
            except (ValueError, KeyError):
                # Skip events with invalid dates
                continue
        
        return events_needing_reminders
    
    async def get_event_count(self) -> int:
        """Get total count of events"""
        events = await self.fetch_all_events()
        return len(events)
    
    async def get_event_stats(self) -> Dict[str, Any]:
        """Get comprehensive event statistics"""
        all_events = await self.fetch_all_events()
        upcoming = await self.get_upcoming_events()
        past = await self.get_past_events()
        
        next_event = None
        if upcoming:
            next_event = {
                "title": upcoming[0]["title"],
                "date": upcoming[0]["formatted_date"],
                "link": upcoming[0]["link"]
            }
        
        return {
            "total_events": len(all_events),
            "upcoming_events": len(upcoming),
            "past_events": len(past),
            "next_event": next_event
        }