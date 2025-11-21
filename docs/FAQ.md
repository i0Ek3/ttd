# ❓ Frequently Asked Questions (FAQ)

## 🔍 General Questions

### Q: What is TTD?
**A:** TTD is a modern, user-friendly application that allows you to download TikTok videos to your computer. It features a clean interface with TikTok-themed colors and multiple download engines for maximum compatibility.

### Q: Is TTD free to use?
**A:** Yes! TTD is free for personal use under the AGPLv3 license. Commercial use requires a separate license. See `DUAL_LICENSING_DETAILS.txt` for more information.

### Q: What platforms does TTD support?
**A:** TTD works on Windows, macOS, and Linux systems with Python 3.7 or higher.

### Q: Is it safe to use?
**A:** Yes, TTD is completely safe. It doesn't collect personal data, doesn't contain malware, and only connects to TikTok servers for downloads. Always download from the official GitHub repository.

---

## 📥 Download Questions

### Q: What video formats can I download?
**A:** TTD downloads videos in MP4 format, which is compatible with most devices and media players.

### Q: Can I download videos without watermarks?
**A:** Yes! When using the yt-dlp engine (recommended), videos are downloaded without TikTok watermarks.

### Q: What quality options are available?
**A:** TTD automatically downloads in the highest available quality (up to 1080p) to ensure you get the best possible video quality with optimal file size.

### Q: Can I download private videos?
**A:** No, TTD can only download publicly available videos. Private or deleted videos cannot be accessed.

### Q: Can I download multiple videos at once?
**A:** Currently, TTD downloads one video at a time. Batch downloading is not supported in this version.

### Q: Why do some downloads fail?
**A:** Downloads may fail due to:
- Invalid or expired URLs
- Private/deleted videos
- Regional restrictions
- Network connectivity issues
- Outdated download engines

**Solution:** Try switching engines or updating libraries.

---

## 🔧 Technical Questions

### Q: What's the difference between the download engines?
**A:** 
- **yt-dlp (Recommended)**: Higher success rate, watermark-free downloads, more stable
- **TikTok API**: Faster downloads, lower resource usage, but may include watermarks

### Q: How do I update the download engines?
**A:** Click the "Update Libraries" button in the application, or run:
```bash
pip install --upgrade yt-dlp
```

### Q: Where are downloaded videos saved?
**A:** By default, videos are saved to a "Downloads" folder in the application directory. You can change this using the "Browse" button.

### Q: Can I change the file names?
**A:** Currently, files are automatically named using the video title from TikTok. Custom naming is not available in this version.

### Q: Why is the application slow to start?
**A:** First-time startup may be slower as Python loads all dependencies. Subsequent launches should be faster.

---

## 🛠️ Troubleshooting

### Q: "Python not found" error - what do I do?
**A:** Install Python 3.7+ from [python.org](https://python.org) and make sure to check "Add Python to PATH" during installation.

### Q: "Module not found" errors during setup?
**A:** Try:
1. Run `python setup.py` again
2. Install manually: `pip install customtkinter pillow yt-dlp requests`
3. Use `python -m pip install` instead of just `pip`

### Q: The application window doesn't appear?
**A:** 
1. Check if Python is properly installed
2. Try running `python test_app.py` to check components
3. Ensure you have a desktop environment (not just command line)
4. Try running as administrator

### Q: Downloads keep failing with yt-dlp?
**A:** 
1. Update yt-dlp: Click "Update Libraries"
2. Try the TikTok API engine instead
3. Check if the video URL is still valid
4. Verify your internet connection

### Q: "Permission denied" when downloading?
**A:** 
1. Choose a different output folder (like Desktop or Documents)
2. Run the application as administrator
3. Check if antivirus is blocking the download

### Q: The interface looks broken or weird?
**A:** 
1. Update CustomTkinter: `pip install --upgrade customtkinter`
2. Check your display scaling settings
3. Try running on a different monitor if using multiple displays

---