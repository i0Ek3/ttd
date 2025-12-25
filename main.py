#!/usr/bin/env python3
"""
TTD
A modern TikTok content downloader with clean UI
"""

import pyperclip
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import os
import sys
import json
from pathlib import Path
import webbrowser
from datetime import datetime

# Import downloader engines
import yt_dlp
from engines.yt_dlp_engine import YtDlpEngine
from engines.tiktok_api_engine import TikTokApiEngine
from ui.components import ModernButton, InfoTooltip, ProgressBar
from ui.styles import ModernStyle
from utils.validator import URLValidator
from utils.logger import Logger

def get_resource_path(relative_path):
    """
    Get the absolute path of the resource file
    Applicable to development environments and PyInstaller packaged environments
    """
    try:
        # PyInstaller creates temporary folder, store path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

class HikariTikTokDownloader:
    def __init__(self):
        # Initialize CustomTkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        # Set white background
        self.root.configure(fg_color="white", border_color="#C6C6C8")
        
        self.setup_window()
        self.setup_variables()
        self.setup_engines()

        self.last_clipboard_content = ""
        self.clipboard_monitor_enabled = True
        self.clipboard_check_interval = 500

        self.create_ui()

        self.root.after(100, self.start_clipboard_monitor)
        
    def setup_window(self):
        """Configure main window"""
        self.root.title("TTD - Modified by i0Ek3")
        self.root.geometry("720x700")
        self.root.minsize(720, 700)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (720 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"720x700+{x}+{y}")
        
    def setup_variables(self):
        """Initialize variables"""
        self.url_var = tk.StringVar()

        # Settings file path
        user_home = Path.home()
        app_data_dir = user_home / ".ttd"
        app_data_dir.mkdir(exist_ok=True)
        self.settings_file = str(app_data_dir / "settings.json")

        # Create Downloads folder in program directory (default)
        self.default_downloads_path = str(user_home / "Downloads" / "TTD")
        if not os.path.exists(self.default_downloads_path):
            try:
                os.makedirs(self.default_downloads_path)
            except Exception:
                self.default_downloads_path = str(user_home / "Downloads")
                self.logger.warning(f"Create default download director failed, will use: {self.default_downloads_path}")
                     
        # Load settings or use defaults
        settings = self.load_settings()
        last_output_dir = settings.get("last_output_dir", self.default_downloads_path)
        
        # Verify the last output directory still exists
        if not os.path.exists(last_output_dir):
            last_output_dir = self.default_downloads_path
        
        self.output_dir = tk.StringVar(value=last_output_dir)
        self.engine_var = tk.StringVar(value=settings.get("engine", "yt-dlp"))
        self.video_name_var = tk.StringVar(value="")
        self.quality_var = tk.StringVar(value="best")
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready")
        
        self.last_clipboard_content = ""
        self.clipboard_monitor_enabled = True
        self.clipboard_check_interval = 500
        
        from utils.logger import Logger
        from utils.validator import URLValidator
        
        self.logger = Logger()
        self.validator = URLValidator()
        
    def setup_engines(self):
        """Initialize download engines"""
        self.engines = {
            "yt-dlp": YtDlpEngine(),
            "tiktok-api": TikTokApiEngine()
        }
        
    def create_ui(self):
        """Create the main user interface"""
        # Main container with white background
        main_frame = ctk.CTkFrame(self.root, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create two columns
        self.create_left_column(main_frame)
        self.create_right_column(main_frame)

    def start_clipboard_monitor(self):
        """
        Enable clipboard monitoring
        Use polling to periodically check the clipboard contents
        """
        if not self.clipboard_monitor_enabled:
            return
        
        try:
            current_clipboard = pyperclip.paste().strip()
            if current_clipboard != self.last_clipboard_content:
                if current_clipboard and self.is_tiktok_url(current_clipboard):
                    # Automatically paste only when the current URL input box is empty or the content is different
                    current_url = self.url_var.get().strip()
                    
                    if not current_url or current_url != current_clipboard:
                        self.auto_paste_url(current_clipboard)
                
                # Update recorded clipboard content
                self.last_clipboard_content = current_clipboard
        
        except Exception as e:
            print(f"Clipboard monitoring error: {e}")
        
        # Continue monitoring (polling)
        self.root.after(self.clipboard_check_interval, self.start_clipboard_monitor)
        
    def auto_paste_url(self, url):
        try:
            self.url_var.set(url)
            self.on_url_change()
            self.status_var.set(f"TikTok links detected")
            self.logger.info(f"Automatically paste TikTok link: {url}")
            print(f"✅ Automatically paste TikTok link: {url}")
        except Exception as e:
            self.logger.error(f"Automatically paste failed: {str(e)}")
            print(f"❎ Automatically paste failed: {str(e)}")

    def create_left_column(self, parent):
        """Create left column with main controls"""
        left_frame = ctk.CTkFrame(parent, corner_radius=15, fg_color="#F8F9FA")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Title
        title_label = ctk.CTkLabel(
            left_frame, 
            text="TTD",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Disclaimer
        disclaimer_frame = ctk.CTkFrame(left_frame, fg_color="#FFF3CD", corner_radius=10)
        disclaimer_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        disclaimer_text = ctk.CTkLabel(
            disclaimer_frame,
            text="⚠️ IMPORTANT: Only download your own content or content you have permission to download.",
            font=ctk.CTkFont(size=12),
            text_color="#856404",
            wraplength=300
        )
        disclaimer_text.pack(pady=10, padx=10)
        
        # URL Input Section
        self.create_url_section(left_frame)
        
        # Engine Selection
        self.create_engine_section(left_frame)

        # Video Name Input
        self.create_video_name_section(left_frame)
        
        # Quality Selection
        self.create_quality_section(left_frame)
        
        # Output Directory
        self.create_output_section(left_frame)
        
        # Download Button
        self.create_download_section(left_frame)
        
    def create_right_column(self, parent):
        """Create right column with status and diagnostics"""
        right_frame = ctk.CTkFrame(parent, corner_radius=15, fg_color="#F8F9FA", width=280)
        right_frame.pack(side="right", fill="both", padx=(15, 0))
        right_frame.pack_propagate(False)  # Maintain fixed width
        
        # Content Detector
        self.create_detector_section(right_frame)
        
        # Progress Section
        self.create_progress_section(right_frame)
        
        # Support Development Section
        self.create_support_section(right_frame)
        
        # Credits
        self.create_credits_section(right_frame)
        
    def create_url_section(self, parent):
        """Create URL input section"""
        url_frame = ctk.CTkFrame(parent, fg_color="transparent")
        url_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        url_label = ctk.CTkLabel(url_frame, text="TikTok URL:", font=ctk.CTkFont(size=14, weight="bold"))
        url_label.pack(anchor="w")
        
        self.url_entry = ctk.CTkEntry(
            url_frame,
            textvariable=self.url_var,
            placeholder_text="Paste TikTok URL here...",
            height=35,
            corner_radius=8
        )
        self.url_entry.pack(fill="x", pady=(5, 0))
        self.url_entry.bind("<KeyRelease>", self.on_url_change)

    @staticmethod
    def is_tiktok_url(url):
        """
        Check if a string is a TikTok link using regular expression.
        Support formats:
        - https://www.tiktok.com/@username/video/1234567890
        - https://tiktok.com/@username/video/1234567890
        - https://vm.tiktok.com/ZMxxxxxxx/
        - https://vt.tiktok.com/ZTxxxxxxx/
        - https://www.tiktok.com/t/ZTxxxxxxx/
        - https://m.tiktok.com/v/1234567890.html
        """

        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        patterns = [
            # Standard link: @username/video/num_id
            r'^https?://(?:www\.|m\.)?tiktok\.com/@[\w.-]+/video/\d+',
            
            # Short link: vm.tiktok.com or vt.tiktok.com
            r'^https?://(?:vm|vt)\.tiktok\.com/[A-Za-z0-9]+',
            
            # tShort link: www.tiktok.com/t/
            r'^https?://(?:www\.)?tiktok\.com/t/[A-Za-z0-9]+',
            
            # Mobile-end short link:: m.tiktok.com/v/
            r'^https?://m\.tiktok\.com/v/\d+(?:\.html)?',
        ]

        for pattern in patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        
        return False

    def create_engine_section(self, parent):
        """Create engine selection section"""
        engine_frame = ctk.CTkFrame(parent, fg_color="transparent")
        engine_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        engine_label = ctk.CTkLabel(engine_frame, text="Download Engine:", font=ctk.CTkFont(size=14, weight="bold"))
        engine_label.pack(anchor="w")
        
        engine_control_frame = ctk.CTkFrame(engine_frame, fg_color="transparent")
        engine_control_frame.pack(fill="x", pady=(5, 0))
        
        self.engine_combo = ctk.CTkComboBox(
            engine_control_frame,
            variable=self.engine_var,
            values=["yt-dlp", "tiktok-api"],
            height=30,
            corner_radius=8,
            state="readonly"
        )
        self.engine_combo.pack(side="left", fill="x", expand=True)
        
        # Info button for engines
        info_btn = ctk.CTkButton(
            engine_control_frame,
            text="ℹ️",
            width=30,
            height=30,
            corner_radius=15,
            command=self.show_engine_info
        )
        info_btn.pack(side="right", padx=(5, 0))

    def create_video_name_section(self, parent):
        """Create video name input section"""
        video_name_frame = ctk.CTkFrame(parent, fg_color="transparent")
        video_name_frame.pack(fill="x", padx=20, pady=(0, 15))
    
        video_name_label = ctk.CTkLabel(
            video_name_frame, 
            text="Video Name:", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        video_name_label.pack(anchor="w")
    
        from ui.styles import ModernStyle
        self.video_name_textbox = ctk.CTkTextbox(
            video_name_frame,
            height=50,
            wrap="word",
            **ModernStyle.TEXTBOX_STYLE
        )
        self.video_name_textbox.pack(fill="x", pady=(5, 0))

        # Initialize text box content
        self.video_name_textbox.insert("end", self.video_name_var.get())

        # Bind content change event
        self.video_name_textbox.bind("<<Modified>>", self.on_video_name_change)

    def on_video_name_change(self, event=None):
        """Synchronize text box content to variable"""
        content = self.video_name_textbox.get("1.0", "end-1c")
        self.video_name_var.set(content)
        # Reset the modified flag so the event triggers again on next edit
        self.video_name_textbox.edit_modified(False)

    def create_quality_section(self, parent):
        """Create quality selection section"""
        quality_frame = ctk.CTkFrame(parent, fg_color="transparent")
        quality_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        quality_label = ctk.CTkLabel(quality_frame, text="Quality:", font=ctk.CTkFont(size=14, weight="bold"))
        quality_label.pack(anchor="w")
        
        quality_control_frame = ctk.CTkFrame(quality_frame, fg_color="transparent")
        quality_control_frame.pack(fill="x", pady=(5, 0))
        
        self.quality_combo = ctk.CTkComboBox(
            quality_control_frame,
            variable=self.quality_var,
            values=["best"],
            height=30,
            corner_radius=8,
            state="readonly"
        )
        self.quality_combo.pack(side="left", fill="x", expand=True)
        
        # Info button for quality
        quality_info_btn = ctk.CTkButton(
            quality_control_frame,
            text="ℹ️",
            width=30,
            height=30,
            corner_radius=15,
            command=self.show_quality_info
        )
        quality_info_btn.pack(side="right", padx=(5, 0))
        
    def create_output_section(self, parent):
        """Create output directory section"""
        output_frame = ctk.CTkFrame(parent, fg_color="transparent")
        output_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        output_label = ctk.CTkLabel(output_frame, text="Output Folder:", font=ctk.CTkFont(size=14, weight="bold"))
        output_label.pack(anchor="w")
        
        output_control_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_control_frame.pack(fill="x", pady=(5, 0))
        
        self.output_entry = ctk.CTkEntry(
            output_control_frame,
            textvariable=self.output_dir,
            height=30,
            corner_radius=8
        )
        self.output_entry.pack(side="left", fill="x", expand=True)
        
        default_btn = ctk.CTkButton(
            output_control_frame,
            text="Default",
            width=65,
            height=30,
            corner_radius=8,
            command=self.set_default_folder
        )
        default_btn.pack(side="right", padx=(5, 0))
        
        browse_btn = ctk.CTkButton(
            output_control_frame,
            text="Browse",
            width=70,
            height=30,
            corner_radius=8,
            command=self.browse_output_folder
        )
        browse_btn.pack(side="right", padx=(5, 0))
        
        open_btn = ctk.CTkButton(
            output_control_frame,
            text="Open",
            width=60,
            height=30,
            corner_radius=8,
            command=self.open_output_folder
        )
        open_btn.pack(side="right", padx=(5, 0))
        
    def create_download_section(self, parent):
        """Create download button section"""
        download_frame = ctk.CTkFrame(parent, fg_color="transparent")
        download_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        # Main download button
        self.download_btn = ctk.CTkButton(
            download_frame,
            text="Download Content",
            height=45,
            corner_radius=12,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#FF0050",  # TikTok pink
            hover_color="#E6004A",
            text_color="white",  # White text color
            text_color_disabled="white",  # White text when disabled
            command=self.start_download
        )
        self.download_btn.pack(fill="x", pady=(0, 10))
        
        # Update libraries button
        self.update_btn = ctk.CTkButton(
            download_frame,
            text="Update Libraries",
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#FF0050",  # TikTok Pink
            hover_color="#E6004A",
            text_color="white",  # White text color
            command=self.update_libraries
        )
        self.update_btn.pack(fill="x")
    
    def create_detector_section(self, parent):
        """Create content detector section"""
        detector_frame = ctk.CTkFrame(parent, corner_radius=10, fg_color="white")
        detector_frame.pack(fill="x", padx=15, pady=(20, 12))
        
        detector_label = ctk.CTkLabel(
            detector_frame,
            text="Content Detector",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        detector_label.pack(pady=(15, 5))
        
        from ui.components import StatusIndicator
        self.status_indicator = StatusIndicator(detector_frame, fg_color="transparent")
        self.status_indicator.pack(pady=(0, 15))
        
    def create_progress_section(self, parent):
        """Create progress section"""
        progress_frame = ctk.CTkFrame(parent, corner_radius=10, fg_color="white")
        progress_frame.pack(fill="x", padx=15, pady=(0, 12))
        
        progress_label = ctk.CTkLabel(
            progress_frame,
            text="Download Progress",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        progress_label.pack(pady=(15, 5))
        
        from ui.components import ProgressBar
        self.progress_bar = ProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 5))
        
        self.status_label = ctk.CTkLabel(
            progress_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=11),
            text_color="#666666"
        )
        self.status_label.pack(pady=(0, 15))
        
    def create_support_section(self, parent):
        """Create support development section"""
        support_frame = ctk.CTkFrame(parent, corner_radius=10, fg_color="white")
        support_frame.pack(fill="x", padx=12, pady=(0, 18))
        
        support_label = ctk.CTkLabel(
            support_frame,
            text="👍🏻 Support Development",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        support_label.pack(pady=(20, 8))
        
        support_text = ctk.CTkLabel(
            support_frame,
            text="If you find TTD useful, consider\nsupporting its development!",
            font=ctk.CTkFont(size=12),
            text_color="#666666",
            justify="center"
        )
        support_text.pack(pady=(0, 15))
        
        # Ko-fi button
        kofi_btn = ctk.CTkButton(
            support_frame,
            text="👍🏻 Give me a like on GitHub",
            height=40,
            corner_radius=10,
            fg_color="#FF5E5B",  # Ko-fi red color
            hover_color="#E54B47",
            text_color="white",  # Explicit white text color
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: webbrowser.open("https://github.com/i0Ek3/ttd")
        )
        kofi_btn.pack(fill="x", padx=18, pady=(0, 15))
        
        thanks_label = ctk.CTkLabel(
            support_frame,
            text="Thank you for your support! 🖤",
            font=ctk.CTkFont(size=11),
            text_color="#999999"
        )
        thanks_label.pack(pady=(0, 20))
        
    def create_credits_section(self, parent):
        """Create credits section"""
        credits_frame = ctk.CTkFrame(parent, corner_radius=10, fg_color="white")
        credits_frame.pack(fill="x", padx=12, pady=(0, 20))
        
        credits_label = ctk.CTkLabel(
            credits_frame,
            text="Credits",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        credits_label.pack(pady=(18, 8))
        
        app_info = ctk.CTkLabel(
            credits_frame,
            text="Hikari TikTok Downloader - Gary19gts\nTTD - Modified by i0Ek3 (202511)\n",
            font=ctk.CTkFont(size=11),
            text_color="#666666",
            justify="center"
        )
        app_info.pack(pady=(0, 12))
        
        # Credits button
        credits_btn = ctk.CTkButton(
            credits_frame,
            text="Special Thanks",
            width=120,
            height=32,
            corner_radius=8,
            command=self.show_credits
        )
        credits_btn.pack(pady=(0, 18))
        
    # Event handlers and utility methods
    def on_url_change(self, event=None):
        """Handle URL input change"""
        url = self.url_var.get().strip()

        # Clear the previous video name
        self.video_name_var.set("")

        if url:
            if self.is_tiktok_url(url):
                self.status_indicator.set_status("success", "Content detected")
                self.logger.info(f"Valid URL detected: {url}")

                # Fetch video info in a separate thread to avoid blocking UI
                info_thread = threading.Thread(
                    target=self._fetch_video_info,
                    args=(url,),
                    daemon=True
                )
                info_thread.start()
            else:
                self.status_indicator.set_status("error", "No content detected")
                self.logger.warning(f"Invalid URL format")
        else:
            self.status_indicator.set_status("error", "No content detected")
    
    # Fetch video metadata
    def _fetch_video_info(self, url):
        """
        Fetch video metadata using yt-dlp to auto-fill the video name.
        This method should be called from a thread to avoid freezing the UI.
        """
        if not url:
            return 
        
        self.logger.info(f"Fetching video info for URL: {url}")

        current_engine_name = self.engine_var.get()
        current_engine = self.engines.get(current_engine_name)

        if current_engine_name != 'yt-dlp' or not hasattr(current_engine, 'DEFAULT_FILENAME_TEMPLATE'):
            self.logger.warning(f"Cannot fetch custom filename template for engine: {current_engine_name}")
            self.root.after(0, lambda: self._update_video_name_ui(""))
            return
        
        filename_template = current_engine.DEFAULT_FILENAME_TEMPLATE

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                channel = info.get('channel', 'UnknownChannel')
                uploader = info.get('uploader', 'UnknownUploader')
                title = info.get('title', 'UnknownTitle')

                video_name = filename_template % {
                    'channel': channel,
                    'uploader': uploader,
                    'title': title
                }

                safe_video_name_for_ui = re.sub(r'[\\/*?:"<>]', "", video_name)
                self.root.after(0, lambda: self._update_video_name_ui(safe_video_name_for_ui))
                
        except Exception as e:
            error_msg = f"Failed to fetch video info: {e}"
            self.logger.error(error_msg)
            self.root.after(0, lambda: self._update_video_name_ui(""))
            self.root.after(0, lambda: self.status_indicator.set_status("error", "Failed to load video info"))

    def _update_video_name_ui(self, video_name):
        """
        Safely update the video name input field from any thread.
        This is the only method that should modify the video_name_var.
        """

        if video_name:
            self.video_name_textbox.delete("1.0", "end")
            self.video_name_textbox.insert("end", video_name)
            self.status_indicator.set_status("success", "Video info loaded")
        else:
            self.video_name_textbox.delete("1.0", "end")
            self.status_indicator.set_status("error", "No video info available")
    
    def show_engine_info(self):
        """Show engine information tooltip"""
        engine_name = self.engine_var.get()
        engine = self.engines.get(engine_name)
        
        if engine:
            info = engine.get_info()
            advantages_text = "\n• ".join(info['advantages'])
            recommended_text = " (Recommended)" if info['recommended'] else ""
            
            message = f"{info['description']}{recommended_text}\n\nAdvantages:\n• {advantages_text}"
            messagebox.showinfo(f"{info['name']} Engine", message)
    
    def show_quality_info(self):
        """Show quality information"""
        message = "Downloads in the highest available quality (up to 1080p)\n\nThis ensures you get the best possible video quality with optimal file size."
        messagebox.showinfo("Quality Information", message)
    
    def browse_output_folder(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir=self.output_dir.get()
        )
        if folder:
            self.output_dir.set(folder)
            self.save_settings()  # Save the new folder selection
            self.logger.info(f"Output folder changed to: {folder}")
    
    def set_default_folder(self):
        """Set output folder to default Downloads folder"""
        self.output_dir.set(self.default_downloads_path)
        self.save_settings()
        self.logger.info(f"Output folder reset to default: {self.default_downloads_path}")
    
    def load_settings(self):
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load settings: {e}")
        return {}
    
    def save_settings(self):
        """Save current settings to JSON file"""
        try:
            settings = {
                "last_output_dir": self.output_dir.get(),
                "engine": self.engine_var.get(),
                "quality": self.quality_var.get()
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            self.logger.debug("Settings saved successfully")
        except Exception as e:
            self.logger.warning(f"Could not save settings: {e}")
    
    def open_output_folder(self):
        """Open output folder in file explorer"""
        output_path = self.output_dir.get()
        if os.path.exists(output_path):
            if sys.platform == "win32":
                os.startfile(output_path)
            elif sys.platform == "darwin":
                os.system(f"open '{output_path}'")
            else:
                os.system(f"xdg-open '{output_path}'")
        else:
            messagebox.showerror("Error", "Output folder does not exist")
    
    def start_download(self):
        """Start download process"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a TikTok URL")
            return
        
        # Validate URL
        is_valid, message = self.validator.is_valid_tiktok_url(url)
        if not is_valid:
            messagebox.showerror("Invalid URL", message)
            return
        
        # Check output directory
        output_path = self.output_dir.get()
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create output directory: {e}")
                return
        
        # Disable download button
        self.download_btn.configure(state="disabled", text="Downloading...")
        
        # Download logic
        custom_video_name = self.video_name_textbox.get("1.0", "end-1c").strip()
        
        # Start download in separate thread
        download_thread = threading.Thread(
            target=self._download_worker,
            args=(url, output_path, custom_video_name),
            daemon=True
        )
        download_thread.start()
    
    def _download_worker(self, url, output_path, custom_name):
        """Download worker thread"""
        try:
            engine_name = self.engine_var.get()
            engine = self.engines.get(engine_name)
            quality = self.quality_var.get()
            
            # Use the custom name passed from UI thread
            # custom_name = self.video_name_var.get().strip()
            
            self.logger.info(f"Starting download with {engine_name} engine")
            self.logger.info(f"URL: {url}")
            self.logger.info(f"Quality: {quality}")
            self.logger.info(f"Output: {output_path}")
            
            # Progress callback
            def progress_callback(percent):
                self.root.after(0, lambda: self.progress_bar.set(percent / 100))
            
            # Status callback
            def status_callback(status):
                self.root.after(0, lambda: self.status_var.set(status))
            
            # Perform download
            success, message = engine.download(
                url, output_path, quality, 
                progress_callback, status_callback,
                custom_filename=custom_name
            )
            
            # Update UI on main thread
            self.root.after(0, lambda: self._download_complete(success, message))
            
        except Exception as e:
            error_msg = f"Download failed: {str(e)}"
            self.logger.error(error_msg)
            self.root.after(0, lambda: self._download_complete(False, error_msg))
    
    def _download_complete(self, success, message):
        """Handle download completion"""
        # Re-enable download button
        self.download_btn.configure(state="normal", text="Download Content")
        
        if success:
            self.progress_bar.set(1.0)
            self.status_var.set("Download completed!")
            self.logger.info("Download completed successfully")
            messagebox.showinfo("Success", message)
        else:
            self.progress_bar.set(0)
            self.status_var.set("Download failed")
            self.logger.error(f"Download failed: {message}")
            messagebox.showerror("Download Failed", message)
    
    def show_diagnostics(self):
        """Show diagnostics window"""
        diag_window = ctk.CTkToplevel(self.root)
        diag_window.title("Diagnostics - TTD")
        diag_window.geometry("600x400")
        
        # Log display
        log_frame = ctk.CTkFrame(diag_window)
        log_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        log_label = ctk.CTkLabel(
            log_frame,
            text="Recent Logs",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        log_label.pack(pady=(10, 5))
        
        # Text widget for logs
        log_text = ctk.CTkTextbox(log_frame, wrap="word")
        log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Load recent logs
        recent_logs = self.logger.get_recent_logs()
        if recent_logs:
            log_text.insert("1.0", "\n".join(recent_logs))
        else:
            log_text.insert("1.0", "No logs available")
        
        # Buttons
        button_frame = ctk.CTkFrame(log_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        refresh_btn = ctk.CTkButton(
            button_frame,
            text="Refresh",
            command=lambda: self._refresh_logs(log_text)
        )
        refresh_btn.pack(side="left", padx=(0, 5))
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear Logs",
            command=lambda: self._clear_logs(log_text)
        )
        clear_btn.pack(side="left")
    
    def _refresh_logs(self, log_text):
        """Refresh log display"""
        log_text.delete("1.0", "end")
        recent_logs = self.logger.get_recent_logs()
        if recent_logs:
            log_text.insert("1.0", "\n".join(recent_logs))
        else:
            log_text.insert("1.0", "No logs available")
    
    def _clear_logs(self, log_text):
        """Clear logs"""
        self.logger.clear_logs()
        log_text.delete("1.0", "end")
        log_text.insert("1.0", "Logs cleared")
    
    def show_credits(self):
        """Show credits and acknowledgments window"""
        credits_window = ctk.CTkToplevel(self.root)
        credits_window.title("Credits & Acknowledgments")
        credits_window.geometry("500x600")
        credits_window.configure(fg_color="white")
        
        # Main frame
        main_frame = ctk.CTkFrame(credits_window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Credits & Acknowledgments",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#333333"
        )
        title_label.pack(pady=(10, 20))
        
        # Scrollable frame for credits
        scrollable_frame = ctk.CTkScrollableFrame(main_frame, fg_color="#F8F9FA")
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Developer section
        dev_frame = ctk.CTkFrame(scrollable_frame, corner_radius=10, fg_color="white")
        dev_frame.pack(fill="x", pady=(0, 15))
        
        dev_title = ctk.CTkLabel(
            dev_frame,
            text="🧑‍💻 Developer",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FF0050"
        )
        dev_title.pack(pady=(15, 5))
        
        dev_info = ctk.CTkLabel(
            dev_frame,
            text="Gary19gts\nCreator of Hikari TikTok Downloader\ni0Ek3\nModified to TTD\n\nThank you for using this application!\nBuilt with passion for the community.",
            font=ctk.CTkFont(size=12),
            text_color="#666666",
            justify="center"
        )
        dev_info.pack(pady=(0, 15))
        
        # Libraries section
        lib_frame = ctk.CTkFrame(scrollable_frame, corner_radius=10, fg_color="white")
        lib_frame.pack(fill="x", pady=(0, 15))
        
        lib_title = ctk.CTkLabel(
            lib_frame,
            text="📚 Libraries & Dependencies",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#007AFF"
        )
        lib_title.pack(pady=(15, 10))
        
        libraries_text = """🎨 CustomTkinter
Modern and customizable tkinter library
Created by Tom Schimansky
Provides the beautiful modern interface

🖼️ Pillow (PIL)
Python Imaging Library
Image processing capabilities
Essential for GUI graphics

📥 yt-dlp
Universal video downloader
Fork of youtube-dl with active development
The most reliable TikTok download engine

🌐 Requests
HTTP library for Python
Simple and elegant HTTP requests
Used for API communications

🐍 Python
The programming language that powers it all
Created by Guido van Rossum
Foundation of this entire application"""
        
        lib_info = ctk.CTkLabel(
            lib_frame,
            text=libraries_text,
            font=ctk.CTkFont(size=11),
            text_color="#666666",
            justify="left"
        )
        lib_info.pack(pady=(0, 15), padx=15)
        
        # Special thanks section
        thanks_frame = ctk.CTkFrame(scrollable_frame, corner_radius=10, fg_color="white")
        thanks_frame.pack(fill="x", pady=(0, 15))
        
        thanks_title = ctk.CTkLabel(
            thanks_frame,
            text="🙏 Special Thanks",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#34C759"
        )
        thanks_title.pack(pady=(15, 5))
        
        thanks_text = ctk.CTkLabel(
            thanks_frame,
            text="• Open source community for amazing tools\n• TikTok for creating an engaging platform\n• All users who respect content creators' rights\n• Contributors to the libraries we depend on\n• Everyone who uses this tool responsibly",
            font=ctk.CTkFont(size=12),
            text_color="#666666",
            justify="left"
        )
        thanks_text.pack(pady=(0, 15), padx=15)
        
        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Close",
            height=35,
            corner_radius=8,
            fg_color="#FF0050",
            hover_color="#E6004A",
            command=credits_window.destroy
        )
        close_btn.pack(pady=(10, 0))
       
    def update_libraries(self):
        """Update libraries automatically"""
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Update Libraries",
            "This will update all libraries to their latest versions.\n\nThis may take a few minutes. Continue?",
            icon="question"
        )
        
        if not result:
            return
        
        # Disable update button during process
        self.update_btn.configure(state="disabled", text="Updating...")
        
        # Start update in separate thread
        update_thread = threading.Thread(
            target=self._update_worker,
            daemon=True
        )
        update_thread.start()
    
    def _update_worker(self):
        """Update worker thread"""
        try:
            import subprocess
            
            self.logger.info("Starting library update process")
            
            # List of libraries to update
            libraries = [
                "customtkinter",
                "pillow", 
                "yt-dlp",
                "requests"
            ]
            
            # Update each library
            for lib in libraries:
                self.root.after(0, lambda l=lib: self.status_var.set(f"Updating {l}..."))
                self.logger.info(f"Updating {lib}")
                
                try:
                    # Run pip install --upgrade for each library
                    result = subprocess.run([
                        sys.executable, "-m", "pip", "install", "--upgrade", lib
                    ], capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        self.logger.info(f"Successfully updated {lib}")
                    else:
                        self.logger.warning(f"Failed to update {lib}: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    self.logger.error(f"Timeout updating {lib}")
                except Exception as e:
                    self.logger.error(f"Error updating {lib}: {e}")
            
            # Update UI on main thread
            self.root.after(0, self._update_complete)
            
        except Exception as e:
            error_msg = f"Update failed: {str(e)}"
            self.logger.error(error_msg)
            self.root.after(0, lambda: self._update_complete(False, error_msg))
    
    def _update_complete(self, success=True, message=""):
        """Handle update completion"""
        # Re-enable update button
        self.update_btn.configure(state="normal", text="Update Libraries")
        
        if success:
            self.status_var.set("Libraries updated successfully!")
            self.logger.info("Library update completed successfully")
            messagebox.showinfo(
                "Update Complete", 
                "Libraries have been updated successfully!\n\nRestart the application to use the latest versions."
            )
        else:
            self.status_var.set("Update failed")
            self.logger.error(f"Library update failed: {message}")
            messagebox.showerror("Update Failed", f"Library update failed:\n\n{message}")
        
    def run(self):
        """Start the application"""
        self.logger.info("TTD started")
        
        # Save settings when window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        self.clipboard_monitor_enabled = False
        self.save_settings()
        self.logger.info("TTD closed")
        self.root.destroy()

if __name__ == "__main__":
    app = HikariTikTokDownloader()
    app.run()