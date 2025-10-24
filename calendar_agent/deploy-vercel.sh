#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Lab Miami Calendar Agent - Vercel Deployment${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found! Run ./setup-env.sh first${NC}"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Vercel CLI...${NC}"
    npm install -g vercel
fi

echo -e "${GREEN}1. Setting up Vercel project...${NC}"
echo ""

# Initialize Vercel project if not already done
if [ ! -f .vercel/project.json ]; then
    echo -e "${YELLOW}This appears to be your first deployment.${NC}"
    echo "Follow the prompts to link your project to Vercel:"
    echo ""
    vercel link
else
    echo -e "${GREEN}✓ Vercel project already linked${NC}"
fi

echo ""
echo -e "${GREEN}2. Setting environment variables in Vercel...${NC}"
echo ""

# Function to add environment variable to Vercel
add_env_var() {
    local key=$1
    local value=$2
    local env_type=${3:-"production preview development"}
    
    if [ ! -z "$value" ] && [ "$value" != "" ]; then
        echo -n "   Setting $key..."
        for env in $env_type; do
            vercel env add "$key" "$env" --force <<< "$value" 2>/dev/null
        done
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e "   ${YELLOW}Skipping $key (no value)${NC}"
    fi
}

# Add all environment variables
echo -e "${YELLOW}Adding environment variables to Vercel...${NC}"
add_env_var "TEXTBELT_API_KEY" "$TEXTBELT_API_KEY"
add_env_var "SMS_TO_NUMBER" "$SMS_TO_NUMBER"
add_env_var "LUMA_URL" "$LUMA_URL"
add_env_var "OPENAI_API_KEY" "$OPENAI_API_KEY"
add_env_var "OPENAI_MODEL" "$OPENAI_MODEL"

echo ""
echo -e "${GREEN}3. Deploying to Vercel...${NC}"
echo ""

# Ask for deployment type
echo "Choose deployment type:"
echo "1) Production deployment (main branch)"
echo "2) Preview deployment (for testing)"
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo -e "${YELLOW}Deploying to production...${NC}"
        vercel --prod
        ;;
    2)
        echo -e "${YELLOW}Deploying preview...${NC}"
        vercel
        ;;
    *)
        echo -e "${RED}Invalid choice. Deploying preview by default...${NC}"
        vercel
        ;;
esac

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo -e "${YELLOW}Important next steps:${NC}"
echo ""
echo "1. ${YELLOW}GitHub Actions Setup (for auto-deployment):${NC}"
echo "   Go to your GitHub repo settings > Secrets and add:"
echo "   - VERCEL_TOKEN (get from: https://vercel.com/account/tokens)"
echo "   - VERCEL_ORG_ID (run: vercel whoami)"
echo "   - VERCEL_PROJECT_ID (check .vercel/project.json)"
echo ""
echo "2. ${YELLOW}Test your endpoints:${NC}"
echo "   - /api/sync - Sync events from Luma"
echo "   - /api/remind - Send reminders"
echo "   - /api/digest - Send weekly digest"
echo "   - /api/stats - View statistics"
echo ""
echo "3. ${YELLOW}Monitor logs:${NC}"
echo "   vercel logs --follow"
echo ""
echo -e "${GREEN}Your app is now live on Vercel! 🎉${NC}"