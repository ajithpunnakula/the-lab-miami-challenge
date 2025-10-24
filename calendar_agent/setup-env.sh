#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Lab Miami Calendar Agent - Environment Setup${NC}"
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file already exists. Backing up to .env.backup${NC}"
    cp .env .env.backup
fi

# Copy from example
cp .env.example .env
echo -e "${GREEN}✓ Created .env from .env.example${NC}"
echo ""

# Function to prompt for input with default value
prompt_with_default() {
    local prompt=$1
    local default=$2
    local var_name=$3
    
    if [ -z "$default" ]; then
        read -p "$prompt: " value
    else
        read -p "$prompt [$default]: " value
        value=${value:-$default}
    fi
    
    # Update .env file
    if [ ! -z "$value" ]; then
        sed -i.bak "s|^$var_name=.*|$var_name=$value|" .env
    fi
}

echo -e "${YELLOW}Let's configure your environment variables:${NC}"
echo ""

# TextBelt SMS Configuration
echo -e "${GREEN}1. TextBelt SMS Configuration${NC}"
echo "   Get API key from: https://textbelt.com"
prompt_with_default "   TextBelt API Key" "" "TEXTBELT_API_KEY"
prompt_with_default "   SMS To Number" "2098129451" "SMS_TO_NUMBER"
echo ""

# OpenAI Configuration
echo -e "${GREEN}2. OpenAI Configuration${NC}"
echo "   Get your API key from: https://platform.openai.com/api-keys"
prompt_with_default "   OpenAI API Key" "" "OPENAI_API_KEY"
prompt_with_default "   OpenAI Model" "gpt-3.5-turbo" "OPENAI_MODEL"
echo ""

# Luma Configuration
echo -e "${GREEN}3. Luma Calendar${NC}"
prompt_with_default "   Luma Calendar URL" "https://lu.ma/usr-vZ7w2FE5gUi7f1Y" "LUMA_URL"
echo ""

# No additional configuration needed - using live Luma data
echo ""

# Clean up backup files
rm -f .env.bak

echo -e "${GREEN}✅ Environment setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review your .env file to ensure all values are correct"
echo "2. Install dependencies: pip install -r requirements.txt"
echo "3. Run locally: uvicorn main:app --reload --port 8000"
echo "4. Deploy to Vercel: ./deploy-vercel.sh"
echo ""
echo -e "${GREEN}Your .env file has been created and configured!${NC}"