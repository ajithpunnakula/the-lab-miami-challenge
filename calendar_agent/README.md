# Calendar Sync & Reminder Agent

Automated event sync and SMS reminders for The Lab Miami's Luma calendar.

## Features

- 🔄 Live event fetching from Luma calendar (no storage needed)
- 📱 SMS reminders via TextBelt (24h, 2h, 30min before events)
- ⏰ Live updates every 5 minutes for today's events
- 🤖 AI-powered message generation using OpenAI for engaging reminders
- 📊 Event statistics and engagement tracking
- ⚡ Serverless deployment on Vercel
- 📝 Customizable prompts for different reminder types

## Setup

### 1. Prerequisites

- Python 3.11+
- TextBelt API key for SMS sending
- OpenAI API key for AI-powered message generation
- Vercel account
- The Lab's Luma calendar URL

### 2. Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd calendar_agent

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Edit .env with your credentials
# Run locally
uvicorn main:app --reload --port 8000
```

### 3. TextBelt SMS Setup

1. Sign up for [TextBelt](https://textbelt.com)
2. Purchase SMS credits or get a free quota
3. Copy your API key
4. Configure the recipient phone number (default: 2098129451)

### 4. OpenAI Setup

1. Sign up for [OpenAI](https://platform.openai.com)
2. Generate an API key from the API keys section
3. Add the key to your `.env` file
4. Choose your preferred model (default: gpt-3.5-turbo)

### 5. Vercel Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod

# Set environment variables in Vercel dashboard
# Go to Project Settings > Environment Variables
```

### 6. Environment Variables

Add these to Vercel dashboard:

```
TEXTBELT_API_KEY=your_textbelt_api_key
SMS_TO_NUMBER=2098129451
LUMA_URL=https://lu.ma/usr-vZ7w2FE5gUi7f1Y
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo
```

## API Endpoints

### POST /api/sync
Fetches latest events from Luma calendar (live data).

```bash
curl -X POST https://your-app.vercel.app/api/sync
```

### POST /api/remind
Checks for upcoming events and sends AI-generated SMS reminders via TextBelt.

```bash
curl -X POST https://your-app.vercel.app/api/remind
```

### POST /api/updates
Sends live updates about today's events (every 5 minutes).

```bash
curl -X POST https://your-app.vercel.app/api/updates
```

### POST /api/digest
Sends a weekly digest of upcoming events using AI summarization.

```bash
curl -X POST https://your-app.vercel.app/api/digest
```

### GET /api/stats
Returns event and reminder statistics (live from Luma).

```bash
curl https://your-app.vercel.app/api/stats
```

## Automatic Scheduling

Vercel cron jobs are configured in `vercel.json`:
- **Event sync**: Every 6 hours (light check)
- **Reminder check**: Every 15 minutes
- **Live updates**: Every 5 minutes for today's events
- **Weekly digest**: Monday at 9 AM

## Data Source

All event data is fetched live from Luma - no storage needed! This ensures:
- Always up-to-date information
- No sync issues
- Simpler architecture
- No storage costs

## Testing

```bash
# Test event sync
curl -X POST http://localhost:8000/api/sync

# Test reminder sending (dry run)
curl -X POST http://localhost:8000/api/remind

# Check statistics
curl http://localhost:8000/api/stats
```

## Troubleshooting

### SMS messages not sending
- Verify TextBelt API key is correct
- Check quota remaining in TextBelt dashboard
- Ensure phone number is valid (10-digit US number)
- Check logs: `vercel logs --follow`

### Events not syncing
- Verify Luma URL is publicly accessible
- Check scraper logs for parsing errors
- Ensure event structure matches expected format

### Vercel deployment issues
- Verify Python version is 3.11+
- Check function timeout settings (30s max)
- Review Vercel function logs

## Architecture

```
calendar_agent/
├── main.py              # FastAPI application
├── api/
│   ├── sync.py         # Event synchronization endpoint
│   ├── remind.py       # AI-powered reminder sending
│   ├── digest.py       # Weekly digest generation
│   └── stats.py        # Statistics endpoint
├── utils/
│   ├── luma_scraper.py        # Luma calendar scraper
│   ├── event_service.py       # Event fetching and filtering
│   ├── reminder_tracker.py    # Simple reminder tracking
│   ├── textbelt_sms.py        # TextBelt SMS client
│   └── ai_summarizer.py       # OpenAI message generation
├── prompts.yaml           # AI prompt templates
├── requirements.txt       # Python dependencies
└── vercel.json           # Vercel configuration
```

## AI Message Customization

Edit `prompts.yaml` to customize AI-generated messages for:
- 24-hour reminders
- 2-hour reminders
- 30-minute reminders
- New event announcements
- Weekly digests

The system uses OpenAI to generate engaging, context-aware messages that maintain The Lab Miami's community voice.

## License

MIT