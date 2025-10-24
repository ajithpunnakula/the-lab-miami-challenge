import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
import hashlib
import re
from pydantic import BaseModel, Field

class Event(BaseModel):
    id: str
    title: str
    start_time: str
    formatted_date: str
    link: str
    description: str = ""
    location: str = ""

class LumaScraper:
    def __init__(self, luma_url: str):
        self.luma_url = luma_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def fetch_events(self) -> List[Dict[str, Any]]:
        try:
            response = await self.client.get(self.luma_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            events = []
            
            event_cards = soup.find_all('div', {'class': re.compile(r'event-card|content-card')})
            
            if not event_cards:
                event_cards = soup.find_all('a', href=re.compile(r'/event/'))
            
            for card in event_cards:
                event_data = self._extract_event_data(card)
                if event_data:
                    events.append(event_data)
            
            if not events:
                events = self._fallback_extraction(soup)
            
            return events
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
        finally:
            await self.client.aclose()
    
    def _extract_event_data(self, card) -> Dict[str, Any]:
        try:
            title_elem = card.find(['h2', 'h3', 'h4']) or card.find('div', {'class': re.compile(r'title|name')})
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            if not title:
                title = card.get_text(strip=True)[:100]
            
            link_elem = card if card.name == 'a' else card.find('a')
            link = ""
            if link_elem and link_elem.get('href'):
                href = link_elem['href']
                link = href if href.startswith('http') else f"https://lu.ma{href}"
            
            date_elem = card.find(['time', 'span'], {'class': re.compile(r'date|time')})
            date_text = date_elem.get_text(strip=True) if date_elem else ""
            
            if not date_text:
                date_elem = card.find(text=re.compile(r'\d{1,2}:\d{2}|\w+ \d{1,2}'))
                date_text = str(date_elem) if date_elem else ""
            
            desc_elem = card.find(['p', 'div'], {'class': re.compile(r'desc|summary')})
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            location_elem = card.find(['span', 'div'], {'class': re.compile(r'location|venue')})
            location = location_elem.get_text(strip=True) if location_elem else ""
            
            event_id = hashlib.md5(f"{title}{link}".encode()).hexdigest()[:12]
            
            start_time = self._parse_date(date_text)
            
            return {
                "id": event_id,
                "title": title or "Untitled Event",
                "start_time": start_time,
                "formatted_date": date_text or "Date TBD",
                "link": link or self.luma_url,
                "description": description[:500],
                "location": location
            }
        except Exception as e:
            print(f"Error extracting event data: {e}")
            return None
    
    def _parse_date(self, date_text: str) -> str:
        try:
            patterns = [
                r'(\w+ \d{1,2}, \d{4})',
                r'(\w+ \d{1,2})',
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{1,2}-\d{1,2}-\d{4})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, date_text)
                if match:
                    return datetime.utcnow().isoformat()
            
            return datetime.utcnow().isoformat()
        except:
            return datetime.utcnow().isoformat()
    
    def _fallback_extraction(self, soup) -> List[Dict[str, Any]]:
        events = []
        
        links = soup.find_all('a', href=re.compile(r'lu\.ma|luma'))
        for link in links[:10]:
            title = link.get_text(strip=True)
            if title and len(title) > 5:
                event_id = hashlib.md5(f"{title}{link.get('href', '')}".encode()).hexdigest()[:12]
                events.append({
                    "id": event_id,
                    "title": title,
                    "start_time": datetime.utcnow().isoformat(),
                    "formatted_date": "Date TBD",
                    "link": link.get('href', self.luma_url),
                    "description": "",
                    "location": ""
                })
        
        return events