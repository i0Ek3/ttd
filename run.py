#!/usr/bin/env python3
"""
TTD Launcher
Simple launcher script that checks dependencies and runs the application
"""

import sys
import subprocess
import importlib.util
import os
from pathlib import Path

# Configure console colors
def setup_console_colors():
    """Setup console colors"""
    if sys.platform == "win32":
        os.system('color')

def colored_print(text):
    """Print text with TikTok cyan color"""
    print(f"\033[38;2;0;224;183m{text}\033[0m")

# Setup colors at import
setup_console_colors()

def check_dependency(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    spec = importlib.util.find_spec(import_name)
    return spec is not None

def install_missing_dependencies():
    """Install missing dependencies"""
    required_packages = [
        ('customtkinter', 'customtkinter'),
        ('pillow', 'PIL'),
        ('yt-dlp', 'yt_dlp'),
        ('requests', 'requests')
    ]
    
    missing_packages = []
    
    colored_print("🔍 Checking dependencies...")
    
    for package, import_name in required_packages:
        if not check_dependency(package, import_name):
            missing_packages.append(package)
            colored_print(f"❌ Missing: {package}")
        else:
            colored_print(f"✅ Found: {package}")
    
    if missing_packages:
        colored_print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            colored_print("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            print("\n💡 Try running manually:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
    else:
        colored_print("✅ All dependencies are installed!")
        return True

def create_directories():
    """Create necessary directories"""
    directories = ['logs']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def main():
    """Main launcher function"""
    colored_print("🚀 TTD Launcher")
    colored_print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check and install dependencies
    if not install_missing_dependencies():
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Launch the application
    colored_print("\n🎬 Starting TTD...")
    try:
        from main import HikariTikTokDownloader
        app = HikariTikTokDownloader()
        app.run()
    except ImportError as e:
        print(f"❌ Failed to import main application: {e}")
        print("Make sure main.py is in the same directory")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()