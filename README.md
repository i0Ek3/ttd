# 🎬 TTD

A modern TikTok content downloader with a clean and intuitive interface featuring TikTok-themed design.


![Image](https://github.com/user-attachments/assets/95fa6678-80b9-449c-b80f-f85b85de70b8)

## ✨ Features

- **Modern TikTok-Themed UI** - Clean interface with TikTok colors and modern design elements
- **Multiple Download Engines** - Choose between yt-dlp (recommended) and TikTok API
- **Best Quality Downloads** - Always downloads in the highest available quality (up to 1080p)
- **Watermark-Free Downloads** - Download content without TikTok watermarks using yt-dlp engine
- **Real-time Progress** - Live download progress with speed indicators
- **Content Detection** - Automatic URL validation and content detection
- **Automatic Library Updates** - One-click updates for all dependencies
- **Responsive Design** - Scales beautifully across different screen resolutions

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Windows, macOS, or Linux

### Installation

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/yourusername/hikari-tiktok-downloader.git
   cd hikari-tiktok-downloader
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Launch the application**
   ```bash
   python main.py
   ```

### Manual Installation

If the setup script doesn't work, install dependencies manually:

```bash
pip install customtkinter pillow yt-dlp requests pathlib2
python main.py
```

## 🎯 Usage

1. **Paste TikTok URL** - Copy any TikTok video URL and paste it in the input field
2. **Select Engine** - Choose your preferred download engine (yt-dlp recommended)
3. **Choose Quality** - Select video quality based on your needs
4. **Set Output Folder** - Choose where to save downloaded content
5. **Download** - Click the download button and watch the progress

### Supported URL Formats

- `https://www.tiktok.com/@username/video/1234567890`
- `https://vm.tiktok.com/ZMxxxxxxx/`
- `https://www.tiktok.com/t/ZTxxxxxxx/`
- Mobile TikTok URLs

## 🔧 Download Engines

### yt-dlp (Recommended)
- **Advantages**: Highest success rate, multiple quality options, regular updates, **watermark-free downloads**
- **Best for**: Reliable downloads with maximum compatibility and clean content without TikTok watermarks

### TikTok API
- **Advantages**: Faster download speed, lower resource usage, direct API access
- **Best for**: Quick downloads when yt-dlp is unavailable (may include watermarks)

## 📁 Project Structure

```
hikari-tiktok-downloader/
├── main.py                 # Main application
├── engines/                # Download engines
│   ├── yt_dlp_engine.py   # yt-dlp implementation
│   └── tiktok_api_engine.py # TikTok API implementation
├── ui/                     # User interface components
│   ├── components.py       # Custom UI components
│   └── styles.py          # Modern design constants
├── utils/                  # Utility modules
│   ├── validator.py        # URL validation
│   └── logger.py          # Logging system
├── logs/                   # Application logs
├── requirements.txt        # Dependencies
├── setup.py               # Setup script
└── README.md              # This file
```

## ⚠️ Important Legal Notice

**This application is designed for downloading your own content or content you have explicit permission to download.**

- Only download content you own or have permission to use
- Respect copyright laws and TikTok's Terms of Service
- The developers are not responsible for misuse of this tool
- This tool follows the principle of "tool neutrality" - the responsibility lies with the user

## 🛠️ Troubleshooting

### Common Issues

1. **"No module named 'customtkinter'"**
   ```bash
   pip install customtkinter
   ```

2. **Download fails with yt-dlp**
   - Try updating yt-dlp: `pip install --upgrade yt-dlp`
   - Switch to TikTok API engine
   - Check the diagnostics logs

3. **GUI doesn't appear**
   - Ensure you have a display available
   - Try running with: `python -m tkinter` to test Tkinter

4. **Permission errors**
   - Run as administrator (Windows) or with sudo (Linux/Mac)
   - Check output folder permissions

### Getting Help

1. Check the **Diagnostics** section in the app for detailed logs
2. Look at the log files in the `logs/` directory
3. Ensure your TikTok URL is valid and accessible

## 🔄 Updates

- **v1.2.0** (October 2025)
  - Settings persistence - remembers last download location
  - Default folder button for quick reset
  - Enhanced user experience improvements
- **v1.0.0** (October 2025)
  - Stable release with modern clean UI
  - Multiple download engines with watermark-free downloads
  - Real-time progress tracking
  - Automatic library updates
  - Ko-fi support integration

## 👨‍💻 Credits

**TTD v1.2.0**  
**October 2025**  
**Made by: Gary19gts**

## 📄 License

This project is dual-licensed under AGPL v3 (for open source use) and Proprietary License (for commercial use) - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

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


**Remember**: Always respect content creators' rights and platform terms of service. Happy downloading! 🎉
