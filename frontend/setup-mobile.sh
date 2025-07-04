#!/bin/bash

# ElderWise Mobile App Setup Script

echo "============================================"
echo "ElderWise Mobile App Setup"
echo "============================================"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: This script must be run from the frontend directory${NC}"
    exit 1
fi

# Step 1: Install Capacitor
echo -e "\n${BLUE}Step 1: Installing Capacitor...${NC}"
npm install @capacitor/core @capacitor/cli @capacitor/android @capacitor/ios

# Install additional plugins for elder-friendly features
echo -e "\n${BLUE}Installing Capacitor plugins...${NC}"
npm install @capacitor/app @capacitor/haptics @capacitor/keyboard @capacitor/splash-screen @capacitor/status-bar @capacitor/local-notifications @capacitor/preferences

# Step 2: Build the web app
echo -e "\n${BLUE}Step 2: Building the web app...${NC}"
npm run build

# Step 3: Initialize Capacitor
echo -e "\n${BLUE}Step 3: Initializing Capacitor...${NC}"
npx cap init --web-dir dist --npm-client npm

# Step 4: Add Android platform
echo -e "\n${BLUE}Step 4: Adding Android platform...${NC}"
npx cap add android

# Step 5: Copy web assets to native platforms
echo -e "\n${BLUE}Step 5: Syncing web assets...${NC}"
npx cap sync

# Create Android resources directory structure
echo -e "\n${BLUE}Creating Android resources...${NC}"
mkdir -p android/app/src/main/res/drawable
mkdir -p android/app/src/main/res/mipmap-hdpi
mkdir -p android/app/src/main/res/mipmap-mdpi
mkdir -p android/app/src/main/res/mipmap-xhdpi
mkdir -p android/app/src/main/res/mipmap-xxhdpi
mkdir -p android/app/src/main/res/mipmap-xxxhdpi

echo -e "\n${GREEN}✓ Mobile setup complete!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Install Android Studio"
echo "2. Run: npx cap open android"
echo "3. Build APK in Android Studio (Build → Build Bundle(s) / APK(s) → Build APK(s))"
echo ""
echo -e "${YELLOW}Or build directly using:${NC}"
echo "./build-apk.sh"
echo "============================================"