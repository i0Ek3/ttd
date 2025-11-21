# ❓ Frequently Asked Questions (FAQ)

## 🔍 General Questions

### Q: What is TTD?
**A:** Hikari is a modern, user-friendly application that allows you to download TikTok videos to your computer. It features a clean interface with TikTok-themed colors and multiple download engines for maximum compatibility.

### Q: Is Hikari free to use?
**A:** Yes! Hikari is free for personal use under the AGPLv3 license. Commercial use requires a separate license. See `DUAL_LICENSING_DETAILS.txt` for more information.

### Q: What platforms does Hikari support?
**A:** Hikari works on Windows, macOS, and Linux systems with Python 3.7 or higher.

### Q: Is it safe to use?
**A:** Yes, Hikari is completely safe. It doesn't collect personal data, doesn't contain malware, and only connects to TikTok servers for downloads. Always download from the official GitHub repository.

---

## 📥 Download Questions

### Q: What video formats can I download?
**A:** Hikari downloads videos in MP4 format, which is compatible with most devices and media players.

### Q: Can I download videos without watermarks?
**A:** Yes! When using the yt-dlp engine (recommended), videos are downloaded without TikTok watermarks.

### Q: What quality options are available?
**A:** Hikari automatically downloads in the highest available quality (up to 1080p) to ensure you get the best possible video quality with optimal file size.

### Q: Can I download private videos?
**A:** No, Hikari can only download publicly available videos. Private or deleted videos cannot be accessed.

### Q: Can I download multiple videos at once?
**A:** Currently, Hikari downloads one video at a time. Batch downloading is not supported in this version.

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

## 🔒 Legal & Privacy Questions

### Q: Is it legal to download TikTok videos?
**A:** You should only download:
- Your own videos
- Videos you have explicit permission to download
- Videos for personal use under fair use guidelines

Always respect copyright laws and TikTok's Terms of Service.

### Q: Does Hikari collect my data?
**A:** No! Hikari:
- Doesn't collect personal information
- Doesn't track your usage
- Doesn't send data to external servers
- Only connects to TikTok for downloads

### Q: Can I use Hikari for commercial purposes?
**A:** Commercial use requires a separate license. Contact Gary19gts through Ko-fi for commercial licensing options.

### Q: What about TikTok's Terms of Service?
**A:** Users are responsible for complying with TikTok's Terms of Service. Hikari is a tool - how you use it is your responsibility.

---

## 💼 Business & Licensing

### Q: Can I integrate Hikari into my software?
**A:** Yes, but you'll need a commercial license. Contact Gary19gts for licensing terms and pricing.

### Q: Can I modify the source code?
**A:** Under AGPLv3: Yes, but you must share your modifications under the same license.
Under Commercial License: Yes, with no sharing requirements.

### Q: Can I redistribute Hikari?
**A:** Under AGPLv3: Yes, with full source code and license notices.
Under Commercial License: According to your license agreement.

### Q: How much does a commercial license cost?
**A:** Pricing varies based on use case and company size. Contact Gary19gts through Ko-fi for a quote.

---

## 🆘 Getting Help

### Q: Where can I get support?
**A:** 
1. Check this FAQ first
2. Read the `INSTRUCTIONS.md` file
3. Run `python test_app.py` for diagnostics
4. Check the `logs/` folder for error details
5. Contact Gary19gts through Ko-fi for persistent issues

### Q: How do I report bugs?
**A:** Contact Gary19gts through Ko-fi with:
- Description of the problem
- Steps to reproduce
- Error messages (if any)
- Your system information

### Q: Can I request new features?
**A:** Yes! Feature requests can be submitted through Ko-fi. Popular requests may be added in future versions.

### Q: How often is Hikari updated?
**A:** Updates are released as needed for:
- Bug fixes
- Security patches
- New features
- Compatibility improvements

---

## 💝 Support & Donations

### Q: How can I support the project?
**A:** The best way to support Hikari is through Ko-fi donations. Even small amounts help with development costs and motivation!

### Q: What do donations go toward?
**A:** Donations help with:
- Development time
- Server costs for testing
- Software licenses and tools
- Keeping the project free for personal use

### Q: Are there other ways to help?
**A:** Yes! You can:
- Share Hikari with friends who might find it useful
- Provide feedback and suggestions
- Report bugs you encounter
- Leave positive reviews

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
*If your question isn't answered here, feel free to reach out through Ko-fi!*