# Deployment Guide

## 🚀 Quick Start

### 1. Initial Setup (First Time Only)

```bash
# Clone the repository
git clone <your-repo-url>
cd calendar_agent

# Run the setup script to configure environment variables
./setup-env.sh

# Install dependencies
pip install -r requirements.txt
```

### 2. Local Development

```bash
# Load environment variables
source .env

# Run locally
uvicorn main:app --reload --port 8000

# Test endpoints
curl http://localhost:8000/api/sync
curl http://localhost:8000/api/stats
```

## 🔧 Environment Variables

### Local Development (.env file)

The `.env` file is used for local development and is NOT committed to git. Create it using:

```bash
./setup-env.sh
```

Or manually copy and edit:

```bash
cp .env.example .env
# Edit .env with your values
```

### Required Variables

```env
# TextBelt (SMS)
TEXTBELT_API_KEY=your_textbelt_api_key_here
SMS_TO_NUMBER=2098129451

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-3.5-turbo

# Luma Calendar
LUMA_URL=https://lu.ma/usr-vZ7w2FE5gUi7f1Y
```

## 📦 Vercel Deployment

### Method 1: Using Deployment Script (Recommended)

```bash
# This script will:
# - Set up Vercel project
# - Upload all environment variables
# - Deploy your app
./deploy-vercel.sh
```

### Method 2: Manual Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Link to Vercel project
vercel link

# Push environment variables to Vercel
./sync-vercel-env.sh
# Choose option 2 to push from .env to Vercel

# Deploy to production
vercel --prod
```

### Managing Vercel Environment Variables

Use the sync script for easy management:

```bash
./sync-vercel-env.sh
```

Options:
1. **Pull from Vercel** - Download env vars from Vercel to local .env
2. **Push to Vercel** - Upload your local .env to Vercel
3. **List variables** - Show all Vercel env vars
4. **Remove variable** - Delete a variable from Vercel

Or use Vercel CLI directly:

```bash
# Add a single variable
vercel env add VARIABLE_NAME production

# List all variables
vercel env ls production

# Remove a variable
vercel env rm VARIABLE_NAME production
```

## 🤖 GitHub Actions Auto-Deployment

### Setup (One Time)

1. **Get Vercel Token:**
   - Go to https://vercel.com/account/tokens
   - Create new token
   - Copy the token

2. **Get Project IDs:**
   ```bash
   # Get your org ID
   vercel whoami
   
   # Get project ID (after linking)
   cat .vercel/project.json
   ```

3. **Add GitHub Secrets:**
   - Go to your GitHub repo
   - Settings → Secrets and variables → Actions
   - Add these secrets:
     - `VERCEL_TOKEN` - Your Vercel token
     - `VERCEL_ORG_ID` - Your Vercel org ID
     - `VERCEL_PROJECT_ID` - Your Vercel project ID

### How It Works

- **Push to main/master** → Automatically deploys to production
- **Open PR** → Creates preview deployment with unique URL
- **Update PR** → Updates preview deployment

## 📊 Monitoring

### View Logs

```bash
# Real-time logs
vercel logs --follow

# Last 100 logs
vercel logs -n 100
```

### Check Deployment Status

```bash
# List recent deployments
vercel list

# Get deployment details
vercel inspect [deployment-url]
```

## 🧪 Testing Deployment

### Test Production Endpoints

```bash
# Replace with your actual Vercel URL
PROD_URL="https://your-app.vercel.app"

# Sync events
curl -X POST $PROD_URL/api/sync

# Check stats
curl $PROD_URL/api/stats

# Manually trigger reminder (for testing)
curl -X POST $PROD_URL/api/remind

# Send weekly digest
curl -X POST $PROD_URL/api/digest
```

## 🔄 Updating Environment Variables

### For Local Development

1. Edit `.env` file
2. Restart your local server

### For Vercel (Production)

Option 1: Using script
```bash
./sync-vercel-env.sh
# Choose option 2 to push changes
```

Option 2: Via Vercel Dashboard
1. Go to your project on vercel.com
2. Settings → Environment Variables
3. Add/Edit variables
4. Redeploy for changes to take effect

Option 3: Via CLI
```bash
# Add/update a variable
vercel env add VARIABLE_NAME production

# Redeploy to apply changes
vercel --prod
```

## 🚨 Troubleshooting

### Environment Variables Not Working

```bash
# Check if variables are set in Vercel
vercel env ls production

# Pull latest from Vercel to verify
vercel env pull .env.check
cat .env.check
```

### Deployment Failing

```bash
# Check build logs
vercel logs --scope=build

# Verify Python version
# Should be 3.11+ in vercel.json
```

### SMS Not Sending

1. Verify TextBelt API key in Vercel env vars
2. Check phone number format: `2098129451` (10-digit US number)
3. Verify quota remaining at https://textbelt.com
4. Check logs: `vercel logs --follow`

### Cron Jobs Not Running

1. Verify cron configuration in `vercel.json`
2. Check function logs for errors
3. Ensure timezone settings are correct

## 📝 Development Workflow

1. **Make changes locally**
   ```bash
   # Test with local env
   source .env
   uvicorn main:app --reload
   ```

2. **Commit and push to feature branch**
   ```bash
   git checkout -b feature/my-feature
   git add .
   git commit -m "Add new feature"
   git push origin feature/my-feature
   ```

3. **Create PR** → Preview deployment created automatically

4. **Merge to main** → Production deployment triggered

5. **Monitor deployment**
   ```bash
   vercel logs --follow
   ```

## 🔐 Security Notes

- Never commit `.env` file
- Use different API keys for dev/prod
- Rotate tokens regularly
- Use Vercel's built-in env var encryption
- Restrict TextBelt SMS to known phone numbers

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel CLI Reference](https://vercel.com/docs/cli)
- [FastAPI on Vercel](https://vercel.com/docs/frameworks/nextjs)
- [TextBelt SMS API](https://textbelt.com/docs)
- [OpenAI API Docs](https://platform.openai.com/docs)