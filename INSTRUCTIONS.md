# 📖 TTD - Complete Instructions

## 🚀 Quick Start Guide

### Step 1: Installation
1. **Download** the latest release from GitHub
2. **Extract** all files to a folder of your choice
3. **Run** `setup.py` to install dependencies:
   ```bash
   python setup.py
   ```

### Step 2: Launch the Application
Choose one of these methods:
- **Windows**: Double-click `run.bat`
- **Command Line**: `python main.py`
- **Alternative**: `python run.py`

### Step 3: Download Content
1. **Copy** a TikTok video URL
2. **Paste** it in the URL field
3. **Select** your preferred settings
4. **Click** "Download Content"

---

## 🔧 Detailed Setup Instructions

### System Requirements
- **Python 3.7+** (Download from [python.org](https://python.org))
- **Windows 10+** / **macOS 10.14+** / **Linux Ubuntu 18.04+**
- **Internet connection** for downloads
- **50MB free space** minimum

### Manual Installation (if setup.py fails)
```bash
# Install dependencies one by one
pip install customtkinter
pip install pillow
pip install yt-dlp
pip install requests

# Verify installation
python test_app.py
```

### Troubleshooting Installation
**Problem**: "Python not found"
- **Solution**: Install Python from python.org and add to PATH

**Problem**: "Permission denied"
- **Windows**: Run Command Prompt as Administrator
- **macOS/Linux**: Use `sudo pip install` or virtual environment

**Problem**: "Module not found"
- **Solution**: Try `python -m pip install [package_name]`

---

## 🎯 How to Use

### Understanding the Interface

#### Left Panel - Main Controls
- **URL Input**: Paste TikTok video URLs here
- **Engine Selection**: Choose download method
- **Quality Settings**: Select video resolution
- **Output Folder**: Choose where files are saved
- **Download Button**: Start the download process

#### Right Panel - Status & Info
- **Content Detector**: Shows if URL is valid
- **Progress Bar**: Real-time download progress
- **Support Section**: Ko-fi donation link
- **Credits**: App information

### Supported URL Formats
✅ **Standard URLs**:
```
https://www.tiktok.com/@username/video/1234567890
https://tiktok.com/@username/video/1234567890
```

✅ **Short URLs**:
```
https://vm.tiktok.com/ZMxxxxxxx/
https://www.tiktok.com/t/ZTxxxxxxx/
```

✅ **Mobile URLs**:
```
https://m.tiktok.com/v/1234567890.html
```

❌ **NOT Supported**:
- Profile URLs (@username)
- Hashtag URLs (#hashtag)
- Live stream URLs
- Private/deleted videos

### Download Engines Explained

#### YT-DLP Engine (Recommended) ⭐
- **Best for**: Reliable downloads, watermark-free content
- **Pros**: 
  - Highest success rate (95%+)
  - No watermarks on videos
  - Multiple quality options
  - Regular updates
- **Cons**: 
  - Slightly slower
  - Larger file sizes

#### TikTok API Engine
- **Best for**: Quick downloads when yt-dlp fails
- **Pros**:
  - Faster download speed
  - Lower resource usage
  - Direct API access
- **Cons**:
  - May include watermarks
  - Lower success rate
  - Limited quality options

### Quality Settings Guide

Hikari automatically downloads videos in the highest available quality (up to 1080p) to ensure optimal video quality and file size balance. This eliminates the need to choose between different quality options and guarantees you always get the best possible result.

---

## ⚙️ Advanced Configuration

### Settings Persistence
The app remembers:
- Last output folder
- Preferred engine
- Quality selection
- Window position

Settings are saved in `settings.json` (auto-created).

### Custom Output Folders
- **Default**: `Downloads/` folder in app directory
- **Custom**: Use "Browse" button to select any folder
- **Reset**: "Default" button returns to app folder

### Batch Downloads
Currently not supported. Download videos one at a time for best results.

### Update Management
- **Auto-check**: App checks for library updates
- **Manual update**: Click "Update Libraries" button
- **Frequency**: Check monthly for best compatibility

---

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### "Download Failed" Error
1. **Check URL**: Ensure it's a valid TikTok video URL
2. **Try different engine**: Switch between yt-dlp and TikTok API
3. **Update libraries**: Click "Update Libraries" button
4. **Check internet**: Verify connection is stable
5. **Check permissions**: Ensure write access to output folder

#### "No Content Detected"
- **Invalid URL**: URL format not recognized
- **Private video**: Video may be private or deleted
- **Regional restrictions**: Video not available in your region
- **Copy error**: Re-copy the URL from TikTok

#### Application Won't Start
1. **Python version**: Ensure Python 3.7+ is installed
2. **Dependencies**: Run `python test_app.py` to check
3. **Permissions**: Try running as administrator
4. **Display**: Ensure you have a display/desktop environment

#### Slow Downloads
- **Switch engines**: Try TikTok API engine for speed
- **Check connection**: Verify internet speed
- **Close other apps**: Free up bandwidth
- **Try different engine**: Switch to TikTok API engine for faster downloads

#### Files Not Saving
- **Folder permissions**: Choose a different output folder
- **Disk space**: Ensure sufficient free space
- **Antivirus**: Check if antivirus is blocking
- **Path length**: Avoid very long folder paths

### Getting Help
1. **Check logs**: Look in `logs/` folder for error details
2. **Run diagnostics**: Use built-in diagnostics feature
3. **Test components**: Run `python test_app.py`
4. **Contact support**: Through Ko-fi if issues persist

---

## 📱 Platform-Specific Notes

### Windows
- **Recommended**: Use `run.bat` for easiest startup
- **Icon**: App icon should appear in taskbar
- **Antivirus**: May need to whitelist the application
- **Updates**: Windows Defender might scan downloads

### macOS
- **Security**: May need to allow app in Security & Privacy
- **Python**: Use Homebrew or official installer
- **Permissions**: Grant folder access when prompted

### Linux
- **Dependencies**: May need additional system packages
- **Display**: Requires X11 or Wayland
- **Permissions**: Ensure user has write access to chosen folders

---

## 🎨 Customization

### Themes
Currently supports:
- **Light mode** (default)
- TikTok pink/cyan color scheme
- Modern rounded corners

### File Naming
Downloaded files are named using:
- Video title (cleaned for file system)
- `.mp4` extension
- Special characters removed automatically

---

## 🔒 Privacy & Security

### Data Collection
TTD:
- ✅ **Does NOT** collect personal data
- ✅ **Does NOT** track usage
- ✅ **Does NOT** send data to external servers
- ✅ **Only** connects to TikTok for downloads

### Safe Usage
- Only download content you own or have permission to use
- Respect copyright laws and TikTok's Terms of Service
- Scan downloaded files if you're unsure about their safety
- Keep the application updated for security patches

---

## 💝 Support the Project

Thank you for using **TTD**!  
Made with ❤️ by Gary19gts  

If Hikari has been helpful to you, please consider supporting its development:  

☕ **Buy me a coffee on Ko-fi** → [https://ko-fi.com/gary19gts](https://ko-fi.com/gary19gts)  

✨ Even the smallest donation can bring a big light during these tough times.  
Even $1 can help more than you think 😀🙏

Thank you so much for standing with me! ✨

---

*Last updated: October 2025*  
*Version: 1.2.0*