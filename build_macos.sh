#!/bin/bash

# TTD macOS Packaging Script
# Usage: ./build_macos.sh [architecture]
# Architecture options: arm64 (Apple Silicon) or x86_64 (Intel)

set -e  # Exit immediately on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  TTD macOS Packaging Tool${NC}"
echo -e "${GREEN}======================================${NC}"

# Detect architecture
ARCH=${1:-$(uname -m)}
echo -e "${YELLOW}Target architecture: $ARCH${NC}"

# Clean old files
echo -e "${YELLOW}Cleaning old build files...${NC}"
rm -rf build dist *.spec 2>/dev/null || true

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${RED}Error: PyInstaller is not installed${NC}"
    echo "Please run: pip install pyinstaller"
    exit 1
fi

if ! command -v create-dmg &> /dev/null; then
    echo -e "${RED}Error: create-dmg is not installed${NC}"
    echo "Please run: brew install create-dmg"
    exit 1
fi

# Check icon file
if [ ! -f "TTD.icns" ]; then
    echo -e "${YELLOW}Warning: TTD.icns icon file not found${NC}"
    echo "Default icon will be used"
fi

# Step 1: Package application with PyInstaller
echo -e "${YELLOW}Step 1/3: Packaging application with PyInstaller...${NC}"
pyinstaller --clean --noconfirm \
    --name='TTD' \
    --windowed \
    --icon='TTD.icns' \
    --osx-bundle-identifier='com.i0ek3.ttd' \
    --target-arch=$ARCH \
    --add-data='ui:ui' \
    --add-data='engines:engines' \
    --add-data='utils:utils' \
    --hidden-import='customtkinter' \
    --hidden-import='PIL' \
    --hidden-import='PIL._tkinter_finder' \
    --hidden-import='yt_dlp' \
    --hidden-import='pyperclip' \
    main.py

if [ ! -d "dist/TTD.app" ]; then
    echo -e "${RED}Error: Application packaging failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Application packaged successfully${NC}"

# Step 2: Test application
echo -e "${YELLOW}Step 2/3: Testing application...${NC}"
echo "You can test the application now: open dist/TTD.app"
read -p "Continue to create DMG? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Packaging stopped. Application located at: dist/TTD.app${NC}"
    exit 0
fi

# Step 3: Create DMG
echo -e "${YELLOW}Step 3/3: Creating DMG installer...${NC}"

# Clean old DMG
rm -f dist/TTD*.dmg

# Create DMG
create-dmg \
    --volname "TTD Installer" \
    --volicon "TTD.icns" \
    --window-pos 200 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --icon "TTD.app" 200 190 \
    --hide-extension "TTD.app" \
    --app-drop-link 600 185 \
    --no-internet-enable \
    "dist/TTD-$ARCH.dmg" \
    "dist/TTD.app"

if [ -f "dist/TTD-$ARCH.dmg" ]; then
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}✓ Packaging completed!${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}DMG file location: dist/TTD-$ARCH.dmg${NC}"
    echo -e "${GREEN}File size: $(du -h dist/TTD-$ARCH.dmg | cut -f1)${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Test DMG: open dist/TTD-$ARCH.dmg"
    echo "2. Distribute to users"
else
    echo -e "${RED}Error: DMG creation failed${NC}"
    exit 1
fi