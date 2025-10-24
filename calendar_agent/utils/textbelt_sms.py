import httpx
from typing import Dict, Any, Optional
from utils.ai_summarizer import AISummarizer

class TextBeltSMSClient:
    def __init__(self, api_key: str, to_number: str = "2098129451"):
        self.api_key = api_key
        self.to_number = to_number
        self.base_url = "https://textbelt.com/text"
        self.client = httpx.AsyncClient(timeout=30.0)
        self.ai_summarizer = AISummarizer()
    
    async def send_sms(self, message: str, phone: Optional[str] = None) -> Dict[str, Any]:
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "Missing TextBelt API key"
                }
            
            # Use provided phone or default
            recipient = phone or self.to_number
            
            # SMS optimization - keep under 160 chars for single segment
            if len(message) > 160:
                message = self._optimize_for_sms(message)
            
            data = {
                "phone": recipient,
                "message": message,
                "key": self.api_key
            }
            
            response = await self.client.post(
                self.base_url,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    return {
                        "success": True,
                        "message_id": result.get("textId"),
                        "quota_remaining": result.get("quotaRemaining"),
                        "to": recipient,
                        "service": "TextBelt"
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "Unknown TextBelt error"),
                        "quota_remaining": result.get("quotaRemaining")
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_ai_reminder(self, event: Dict[str, Any], reminder_type: str) -> Dict[str, Any]:
        try:
            message_generator = await self.ai_summarizer.generate_reminder_message(event, reminder_type)
            
            # Optimize message for SMS
            message = self._optimize_for_sms(message_generator.content)
            
            result = await self.send_sms(message)
            result["ai_generated"] = True
            result["tokens_used"] = message_generator.tokens_used
            result["model"] = message_generator.model
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate AI message: {str(e)}"
            }
    
    async def send_ai_announcement(self, event: Dict[str, Any]) -> Dict[str, Any]:
        try:
            message_generator = await self.ai_summarizer.generate_new_event_announcement(event)
            
            # Optimize message for SMS
            message = self._optimize_for_sms(message_generator.content)
            
            result = await self.send_sms(message)
            result["ai_generated"] = True
            result["tokens_used"] = message_generator.tokens_used
            result["model"] = message_generator.model
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate AI announcement: {str(e)}"
            }
    
    async def send_weekly_digest(self, events: list[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            # For SMS, limit to top 3 events
            if len(events) > 3:
                events = events[:3]
            
            message_generator = await self.ai_summarizer.generate_weekly_digest(events)
            
            # Optimize message for SMS
            message = self._optimize_for_sms(message_generator.content)
            
            result = await self.send_sms(message)
            result["ai_generated"] = True
            result["tokens_used"] = message_generator.tokens_used
            result["model"] = message_generator.model
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate weekly digest: {str(e)}"
            }
    
    def _optimize_for_sms(self, message: str) -> str:
        """Optimize message for SMS (160 chars for single segment)"""
        # Remove extra whitespace
        message = " ".join(message.split())
        
        # Keep under 160 chars for single SMS
        if len(message) > 160:
            # Try to cut at a good spot
            truncated = message[:157]
            
            # Look for good cut points
            cut_points = [
                truncated.rfind('.'),
                truncated.rfind('\n'),
                truncated.rfind(' ')
            ]
            
            best_cut = max([p for p in cut_points if p > 100], default=-1)
            
            if best_cut > 0:
                message = message[:best_cut] + "..."
            else:
                message = truncated + "..."
        
        return message
    
    async def verify_configuration(self) -> Dict[str, Any]:
        try:
            if not self.api_key:
                return {
                    "configured": False,
                    "error": "Missing TextBelt API key"
                }
            
            # Test with a simple quota check
            test_data = {
                "phone": self.to_number,
                "message": "Test configuration",
                "key": self.api_key
            }
            
            response = await self.client.post(
                self.base_url,
                data=test_data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "configured": True,
                    "service": "TextBelt",
                    "to_number": self.to_number,
                    "quota_remaining": result.get("quotaRemaining"),
                    "test_sent": result.get("success", False)
                }
            else:
                return {
                    "configured": False,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "configured": False,
                "error": str(e)
            }
    
    async def close(self):
        await self.client.aclose()