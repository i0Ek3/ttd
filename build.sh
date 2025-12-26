#!/bin/bash

# TTD Unified Build Script
# Usage: ./build.sh
# Supports: macOS (DMG), Linux (Deb/AppImage), Windows (Exe)

set -e  # Exit immediately on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Determine Python command
PYTHON_CMD=python3
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD=python3.11
fi
if [ -n "$PYTHON" ]; then
    PYTHON_CMD="$PYTHON"
fi

# Get Version from version.py
if [ -f "version.py" ]; then
    VERSION=$($PYTHON_CMD -c "from version import __version__; print(__version__)")
else
    VERSION="1.0.0"
fi

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  TTD Unified Build Tool v${VERSION}${NC}"
echo -e "${GREEN}======================================${NC}"

# Detect Host OS
HOST_OS=$(uname -s)
ARCH=$(uname -m)

echo -e "${BLUE}Host System: $HOST_OS ($ARCH)${NC}"
echo ""

# Menu
echo "Select target platform:"
echo "1) macOS (DMG)"
echo "2) Linux (Deb/AppImage/Zip)"
echo "3) Windows (Exe)"
echo "4) All (Run all packaging steps)"
read -p "Enter choice [1-4]: " CHOICE

# Functions
check_dependency() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}Error: $1 remains not installed or not in PATH.${NC}"
        return 1
    fi
    return 0
}

clean_build() {
    echo -e "${YELLOW}Cleaning build directories...${NC}"
    rm -rf build dist *.spec 2>/dev/null || true
    # Restore TTD.spec if we deleted it (actually we should keep it if it's our source)
    # Ideally we wouldn't delete TTD.spec, but generic cleanup might. 
    # Let's assume TTD.spec is persistent and shouldn't be deleted.
}

build_macos() {
    echo -e "\n${BLUE}>>> Starting macOS Build...${NC}"
    
    if [[ "$HOST_OS" != "Darwin" ]]; then
        echo -e "${YELLOW}Warning: You are not running on macOS. PyInstaller cannot cross-compile macOS apps from Linux/Windows.${NC}"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then return; fi
    fi

    # Check dependencies
    if ! $PYTHON_CMD -m PyInstaller --version &> /dev/null; then
        echo -e "${RED}PyInstaller not found. Installing...${NC}"
        # Try installing (might fail on managed envs)
        $PYTHON_CMD -m pip install pyinstaller || echo -e "${RED}Install failed. Please install pyinstaller manually (e.g. brew install or venv).${NC}"
    fi

    check_dependency "create-dmg" || echo -e "${YELLOW}create-dmg not found. DMG creation will be skipped. (brew install create-dmg)${NC}"

    # Build
    echo -e "${YELLOW}Step 1: Building .app bundle...${NC}"
    $PYTHON_CMD -m PyInstaller --clean --noconfirm TTD.spec

    # Codesign
    echo -e "${YELLOW}Step 2: Signing application (Ad-hoc)...${NC}"
    codesign --force --deep --sign - dist/TTD.app

    # Create DMG
    if command -v create-dmg &> /dev/null; then
        echo -e "${YELLOW}Step 3: Creating DMG...${NC}"
        DMG_NAME="TTD-${VERSION}-${ARCH}.dmg"
        rm -f "dist/$DMG_NAME"
        
        create-dmg \
            --volname "TTD ${VERSION} Installer" \
            --volicon "TTD.icns" \
            --window-pos 200 120 \
            --window-size 800 400 \
            --icon-size 100 \
            --icon "TTD.app" 200 190 \
            --hide-extension "TTD.app" \
            --app-drop-link 600 185 \
            --no-internet-enable \
            "dist/$DMG_NAME" \
            "dist/TTD.app"
            
        echo -e "${GREEN}✓ macOS Build Complete: dist/$DMG_NAME${NC}"
    else
        echo -e "${YELLOW}Skipping DMG creation (create-dmg missing). App bundle is in dist/TTD.app${NC}"
    fi
}

build_linux() {
    echo -e "\n${BLUE}>>> Starting Linux Build...${NC}"
    
    if [[ "$HOST_OS" != "Linux" ]]; then
        echo -e "${YELLOW}Notice: Native Linux builds are not possible on macOS.${NC}"
        echo -e "Options:"
        echo -e " 1) Use Docker (if installed)"
        echo -e " 2) Use GitHub Actions (Push to GitHub to build automatically)"
        echo -e " 3) Skip"
        read -p "Your choice [1-3]: " LINUX_CHOICE
        
        case $LINUX_CHOICE in
            1)
                # Check if Docker is available
                if ! command -v docker &> /dev/null; then
                    echo -e "${RED}Error: Docker is not installed.${NC}"
                    return 1
                fi
                echo -e "${YELLOW}Step 1: Building Docker image...${NC}"
                docker build -f Dockerfile.linux -t ttd-linux-builder .
                echo -e "${YELLOW}Step 2: Running build in container...${NC}"
                docker run --rm -v "$(pwd)/dist:/app/dist" ttd-linux-builder
                ;;
            2)
                echo -e "${GREEN}Tip: Check .github/workflows/package.yml. Push your code to GitHub to get automated builds.${NC}"
                return
                ;;
            *)
                return
                ;;
        esac
    else
        # Native Linux build
        echo -e "${YELLOW}Step 1: Building executable...${NC}"
        $PYTHON_CMD -m PyInstaller --clean --noconfirm TTD.spec
    fi

    # Packaging
    if [ -d "dist/TTD" ] || [ -f "dist/TTD" ]; then
        echo -e "${YELLOW}Step 2/3: Creating archive...${NC}"
        cd dist
        zip -r "TTD-${VERSION}-linux-x86_64.zip" TTD 2>/dev/null || tar -czf "TTD-${VERSION}-linux-x86_64.tar.gz" TTD
        cd ..
    fi
    echo -e "${GREEN}✓ Linux Build Complete${NC}"
}

build_windows() {
    echo -e "\n${BLUE}>>> Starting Windows Build...${NC}"
    
    if [[ "$HOST_OS" != "MINGW"* && "$HOST_OS" != "CYGWIN"* && "$HOST_OS" != "MSYS"* ]]; then
        echo -e "${YELLOW}Notice: Native Windows builds are not possible on macOS.${NC}"
        echo -e "Options:"
        echo -e " 1) Use Docker (if installed)"
        echo -e " 2) Use GitHub Actions (Push to GitHub to build automatically)"
        echo -e " 3) Skip"
        read -p "Your choice [1-3]: " WIN_CHOICE
        
        case $WIN_CHOICE in
            1)
                if ! command -v docker &> /dev/null; then
                    echo -e "${RED}Error: Docker is not installed.${NC}"
                    return 1
                fi
                echo -e "${YELLOW}Step 1: Building Docker image...${NC}"
                docker build -f Dockerfile.windows -t ttd-windows-builder .
                echo -e "${YELLOW}Step 2: Running build in container...${NC}"
                docker run --rm -v "$(pwd)/dist:/src/dist" ttd-windows-builder
                ;;
            2)
                echo -e "${GREEN}Tip: Check .github/workflows/package.yml. Push your code to GitHub to get automated builds.${NC}"
                return
                ;;
            *)
                return
                ;;
        esac
    else
        # Native Windows build
        $PYTHON_CMD -m PyInstaller --clean --noconfirm TTD.spec
    fi
    
    # Rename output
    if [ -f "dist/TTD.exe" ]; then
        mv "dist/TTD.exe" "dist/TTD-${VERSION}-windows.exe"
        echo -e "${GREEN}✓ Created: dist/TTD-${VERSION}-windows.exe${NC}"
    fi
}


# Execution
case $CHOICE in
    1)
        build_macos
        ;;
    2)
        build_linux
        ;;
    3)
        build_windows
        ;;
    4)
        build_macos
        build_linux
        build_windows
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo -e "\n${GREEN}Build process finished!${NC}"