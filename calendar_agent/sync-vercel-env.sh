#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Sync Environment Variables with Vercel${NC}"
echo ""

# Function to display menu
show_menu() {
    echo "Choose an option:"
    echo "1) Pull environment variables FROM Vercel to local .env"
    echo "2) Push environment variables FROM local .env to Vercel"
    echo "3) List all Vercel environment variables"
    echo "4) Remove an environment variable from Vercel"
    echo "5) Exit"
}

# Function to pull env vars from Vercel
pull_from_vercel() {
    echo -e "${YELLOW}Pulling environment variables from Vercel...${NC}"
    
    # Backup current .env
    if [ -f .env ]; then
        cp .env .env.backup
        echo -e "${GREEN}✓ Backed up current .env to .env.backup${NC}"
    fi
    
    # Pull from Vercel
    vercel env pull .env.vercel
    
    if [ -f .env.vercel ]; then
        mv .env.vercel .env
        echo -e "${GREEN}✓ Successfully pulled environment variables from Vercel${NC}"
        echo -e "${YELLOW}Note: You may need to add any local-only variables back to .env${NC}"
    else
        echo -e "${RED}❌ Failed to pull environment variables${NC}"
    fi
}

# Function to push env vars to Vercel
push_to_vercel() {
    if [ ! -f .env ]; then
        echo -e "${RED}❌ .env file not found!${NC}"
        return
    fi
    
    echo -e "${YELLOW}Pushing environment variables to Vercel...${NC}"
    echo ""
    
    # Read each line from .env
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        if [[ ! "$key" =~ ^#.*$ ]] && [ ! -z "$key" ]; then
            # Remove any quotes from value
            value=$(echo "$value" | sed 's/^["'"'"']//;s/["'"'"']$//')
            
            if [ ! -z "$value" ]; then
                echo -n "   Setting $key..."
                
                # Add to all environments
                for env in production preview development; do
                    vercel env add "$key" "$env" --force <<< "$value" 2>/dev/null
                done
                
                echo -e " ${GREEN}✓${NC}"
            fi
        fi
    done < .env
    
    echo ""
    echo -e "${GREEN}✓ Environment variables pushed to Vercel${NC}"
}

# Function to list env vars
list_env_vars() {
    echo -e "${YELLOW}Listing all Vercel environment variables:${NC}"
    echo ""
    
    for env in production preview development; do
        echo -e "${GREEN}$env environment:${NC}"
        vercel env ls $env
        echo ""
    done
}

# Function to remove env var
remove_env_var() {
    read -p "Enter the environment variable name to remove: " var_name
    
    if [ -z "$var_name" ]; then
        echo -e "${RED}❌ Variable name cannot be empty${NC}"
        return
    fi
    
    echo -e "${YELLOW}Removing $var_name from all environments...${NC}"
    
    for env in production preview development; do
        echo -n "   Removing from $env..."
        vercel env rm "$var_name" "$env" --yes 2>/dev/null
        echo -e " ${GREEN}✓${NC}"
    done
    
    echo -e "${GREEN}✓ $var_name removed from all environments${NC}"
}

# Main loop
while true; do
    show_menu
    read -p "Enter choice [1-5]: " choice
    echo ""
    
    case $choice in
        1)
            pull_from_vercel
            ;;
        2)
            push_to_vercel
            ;;
        3)
            list_env_vars
            ;;
        4)
            remove_env_var
            ;;
        5)
            echo -e "${GREEN}Goodbye! 👋${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option. Please try again.${NC}"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    echo ""
done