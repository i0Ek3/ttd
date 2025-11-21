#!/usr/bin/env python3
"""
Setup script for TTD
Installs required dependencies and sets up the application

Copyright (C) 2025 Gary19gts

This program is dual-licensed:
1. GNU Affero General Public License v3 (AGPLv3) for open source use
2. Proprietary license for commercial/closed source use

For open source use:
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

For commercial licensing, contact Gary19gts.

Author: Gary19gts
"""

import subprocess
import sys
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

def install_requirements():
    """Install required packages"""
    colored_print("🚀 Setting up TTD...")
    colored_print("📦 Installing dependencies...")
    
    try:
        # Install requirements
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        colored_print("✅ Dependencies installed successfully!")
        
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        colored_print("📁 Created logs directory")
        
        colored_print("\n🎉 Setup completed successfully!")
        colored_print("\n🚀 To run the application:")
        colored_print("   python main.py")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("\n💡 Try running:")
        print("   pip install --upgrade pip")
        print("   python setup.py")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    return True

def main():
    """Main setup function"""
    colored_print("=" * 50)
    colored_print("  TTD Setup")
    colored_print("  Version: 1.2.0")
    colored_print("  Made by: Gary19gts")
    colored_print("=" * 50)
    
    if not check_python_version():
        sys.exit(1)
    
    if install_requirements():
        colored_print("\n🎯 Ready to download TikTok content!")
        colored_print("⚠️  Remember: Only download your own content or content you have permission to download.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()