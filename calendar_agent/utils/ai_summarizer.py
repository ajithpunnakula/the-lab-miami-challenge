import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from pydantic import BaseModel

class MessageGenerator(BaseModel):
    content: str
    tokens_used: int
    model: str

class AISummarizer:
    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, Any]:
        prompts_file = Path(__file__).parent.parent / "prompts.yaml"
        if prompts_file.exists():
            with open(prompts_file, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    async def generate_reminder_message(
        self,
        event: Dict[str, Any],
        reminder_type: str = "24_hours"
    ) -> MessageGenerator:
        try:
            prompt_config = self.prompts.get("event_reminder", {})
            system_prompt = prompt_config.get("system", "")
            
            template = prompt_config.get("templates", {}).get(reminder_type, {})
            user_prompt = template.get("user", "").format(
                title=event.get("title", ""),
                date=event.get("formatted_date", ""),
                description=event.get("description", "")[:200],
                location=event.get("location", "The Lab Miami"),
                link=event.get("link", "")
            )
            
            if not user_prompt:
                return self._fallback_message(event, reminder_type)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return MessageGenerator(
                content=response.choices[0].message.content,
                tokens_used=response.usage.total_tokens,
                model=response.model
            )
        except Exception as e:
            print(f"OpenAI error: {e}")
            return self._fallback_message(event, reminder_type)
    
    async def generate_new_event_announcement(
        self,
        event: Dict[str, Any]
    ) -> MessageGenerator:
        try:
            prompt_config = self.prompts.get("new_event", {})
            system_prompt = prompt_config.get("system", "")
            user_prompt = prompt_config.get("user", "").format(
                title=event.get("title", ""),
                date=event.get("formatted_date", ""),
                description=event.get("description", "")[:300],
                location=event.get("location", "The Lab Miami"),
                link=event.get("link", "")
            )
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=200,
                temperature=0.8
            )
            
            return MessageGenerator(
                content=response.choices[0].message.content,
                tokens_used=response.usage.total_tokens,
                model=response.model
            )
        except Exception as e:
            print(f"OpenAI error: {e}")
            return self._fallback_new_event(event)
    
    async def generate_weekly_digest(
        self,
        events: list[Dict[str, Any]]
    ) -> MessageGenerator:
        try:
            prompt_config = self.prompts.get("weekly_digest", {})
            system_prompt = prompt_config.get("system", "")
            
            events_list = "\n".join([
                f"- {e['title']} ({e['formatted_date']})"
                for e in events[:5]
            ])
            
            user_prompt = prompt_config.get("user", "").format(
                events_list=events_list,
                event_count=len(events),
                week_date="this week"
            )
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return MessageGenerator(
                content=response.choices[0].message.content,
                tokens_used=response.usage.total_tokens,
                model=response.model
            )
        except Exception as e:
            print(f"OpenAI error: {e}")
            return self._fallback_digest(events)
    
    async def summarize_description(
        self,
        description: str
    ) -> str:
        try:
            if len(description) < 150:
                return description
            
            prompt_config = self.prompts.get("event_summary", {})
            system_prompt = prompt_config.get("system", "")
            user_prompt = prompt_config.get("user", "").format(
                description=description[:500]
            )
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=50,
                temperature=0.6
            )
            
            return response.choices[0].message.content
        except Exception:
            return description[:150] + "..."
    
    def _fallback_message(self, event: Dict[str, Any], reminder_type: str) -> MessageGenerator:
        reminder_texts = {
            "24_hours": f"📅 Tomorrow: {event['title']}\n🕒 {event['formatted_date']}\n🔗 RSVP: {event['link']}",
            "2_hours": f"⏰ Starting soon! {event['title']}\n🕒 In 2 hours\n📍 {event.get('location', 'The Lab')}\n🔗 {event['link']}",
            "30_minutes": f"🚨 NOW! {event['title']} starts in 30 min!\n🔗 {event['link']}"
        }
        
        return MessageGenerator(
            content=reminder_texts.get(reminder_type, reminder_texts["24_hours"]),
            tokens_used=0,
            model="fallback"
        )
    
    def _fallback_new_event(self, event: Dict[str, Any]) -> MessageGenerator:
        return MessageGenerator(
            content=f"🎉 New Event!\n\n📅 {event['title']}\n🕒 {event['formatted_date']}\n🔗 RSVP: {event['link']}\n\n{event.get('description', '')[:100]}",
            tokens_used=0,
            model="fallback"
        )
    
    def _fallback_digest(self, events: list[Dict[str, Any]]) -> MessageGenerator:
        digest = "📊 This Week at The Lab\n\n"
        for event in events[:5]:
            digest += f"• {event['title']} - {event['formatted_date']}\n"
        digest += f"\n{len(events)} total events this week!"
        
        return MessageGenerator(
            content=digest,
            tokens_used=0,
            model="fallback"
        )