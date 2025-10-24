import os
from datetime import datetime, timedelta
from typing import Dict, Set
from pathlib import Path

class ReminderTracker:
    """Simple file-based reminder tracking to avoid sending duplicate reminders"""
    
    def __init__(self):
        # Use a simple file in temp directory for tracking
        self.tracking_file = Path("/tmp/reminder_tracking.txt")
        self._sent_reminders: Set[str] = set()
        self._load_tracking()
    
    def _load_tracking(self):
        """Load previously sent reminders from file"""
        try:
            if self.tracking_file.exists():
                with open(self.tracking_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and '|' in line:
                            reminder_key, timestamp_str = line.split('|', 1)
                            # Only keep reminders from last 7 days
                            try:
                                timestamp = datetime.fromisoformat(timestamp_str)
                                if datetime.utcnow() - timestamp < timedelta(days=7):
                                    self._sent_reminders.add(reminder_key)
                            except:
                                continue
        except Exception:
            # If file doesn't exist or is corrupted, start fresh
            self._sent_reminders = set()
    
    def _save_tracking(self):
        """Save current tracking state to file"""
        try:
            # Create directory if it doesn't exist
            self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.tracking_file, 'w') as f:
                current_time = datetime.utcnow().isoformat()
                for reminder_key in self._sent_reminders:
                    f.write(f"{reminder_key}|{current_time}\n")
        except Exception:
            # If we can't save, continue without crashing
            pass
    
    def is_reminder_sent(self, reminder_key: str) -> bool:
        """Check if a reminder has already been sent"""
        return reminder_key in self._sent_reminders
    
    def mark_reminder_sent(self, reminder_key: str) -> bool:
        """Mark a reminder as sent"""
        try:
            self._sent_reminders.add(reminder_key)
            self._save_tracking()
            return True
        except Exception:
            return False
    
    def get_reminders_sent_count(self, since: datetime = None) -> int:
        """Get count of reminders sent (simplified - returns total)"""
        return len(self._sent_reminders)
    
    def cleanup_old_reminders(self):
        """Remove old reminder tracking (older than 7 days)"""
        # This is handled automatically in _load_tracking
        self._load_tracking()
        self._save_tracking()