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
import queue
import time
import collections
import os
import sys
import json
from pathlib import Path
import webbrowser
from datetime import datetime

# Import downloader engines
import yt_dlp
from engines.yt_dlp_engine import YtDlpEngine
from ui.components import ModernButton, InfoTooltip, ProgressBar
from ui.styles import ModernStyle
from utils.validator import URLValidator
from ui.styles import ModernStyle
from utils.validator import URLValidator
try:
    from version import __version__
except ImportError:
    __version__ = "1.0.0"

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

        # Clipboard polling runs in a background thread (see start_clipboard_monitor)
        self._clipboard_queue = queue.Queue()
        self._clipboard_stop = threading.Event()
        self._clipboard_thread = None

        # Video-info fetch state: the token invalidates results from stale fetches
        self._fetch_token = 0
        self._fetching = False
        self._fetch_started = 0.0
        self._current_url = ""
        self._in_name_change = False

        # Auto download state
        # (a plain bool mirror is used because the clipboard thread must not touch Tk variables)
        self._auto_download_enabled = bool(self.auto_download_var.get())
        self._auto_queue = collections.deque()   # links copied while busy
        self._auto_pending_token = None          # fetch token that should start a download
        self._downloading = False
        self._download_is_auto = False

        self.create_ui()

        self.root.after(100, self.start_clipboard_monitor)
        
    def setup_window(self):
        """Configure main window"""
        self.root.title(f"TTD v{__version__} by i0Ek3")
        self.root.geometry("720x680")
        self.root.minsize(720, 680)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (720 // 2)
        y = (self.root.winfo_screenheight() // 2) - (680 // 2)
        self.root.geometry(f"720x680+{x}+{y}")
        
    def setup_variables(self):
        """Initialize variables"""
        self.url_var = tk.StringVar()

        # Settings file path
        user_home = Path.home()
        app_data_dir = user_home / ".ttd"
        app_data_dir.mkdir(exist_ok=True)
        self.settings_file = str(app_data_dir / "settings.json")
        self.history_file = str(app_data_dir / "download_history.json")

        # Create Downloads folder in program directory (default)
        self.default_downloads_path = str(user_home / "Downloads" / "TTD")
        if not os.path.exists(self.default_downloads_path):
            try:
                os.makedirs(self.default_downloads_path)
            except Exception:
                self.default_downloads_path = str(user_home / "Downloads")
                print(f"Create default download directory failed, will use: {self.default_downloads_path}")
                     
        # Load settings or use defaults
        settings = self.load_settings()
        last_output_dir = settings.get("last_output_dir", self.default_downloads_path)
        
        # Verify the last output directory still exists
        if not os.path.exists(last_output_dir):
            last_output_dir = self.default_downloads_path
        
        self.output_dir = tk.StringVar(value=last_output_dir)
        self.engine_var = tk.StringVar(value="yt-dlp")
        self.video_name_var = tk.StringVar(value="")
        self.quality_var = tk.StringVar(value="best")
        # "Auto Download": start downloading as soon as a link is auto-pasted
        self.auto_download_var = tk.BooleanVar(value=bool(settings.get("auto_download", False)))
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
            "yt-dlp": YtDlpEngine()
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
        Enable clipboard monitoring.

        The clipboard is polled in a background thread. Calling pyperclip.paste()
        on the Tk main thread can deadlock/freeze the UI when the clipboard is owned
        by this very app (e.g. right after copying text out of the Video Name box),
        because Tk must serve the clipboard request from its own event loop.
        """
        if not self.clipboard_monitor_enabled:
            return

        if self._clipboard_thread is None or not self._clipboard_thread.is_alive():
            self._clipboard_stop.clear()
            self._clipboard_thread = threading.Thread(
                target=self._clipboard_poll_loop, daemon=True
            )
            self._clipboard_thread.start()

        self.root.after(self.clipboard_check_interval, self._process_clipboard_queue)

    def _clipboard_poll_loop(self):
        """Background thread: watch the clipboard, push new TikTok URLs to the queue."""
        last_seen = self.last_clipboard_content
        interval = self.clipboard_check_interval / 1000.0
        first_pass = True
        while not self._clipboard_stop.is_set():
            try:
                content = (pyperclip.paste() or "").strip()
                # The very first read is whatever was in the clipboard before launch:
                # it is still pasted into the URL box (as before), but flagged so that
                # Auto Download does not start a download by itself for it.
                at_startup = first_pass
                first_pass = False
                if content != last_seen:
                    last_seen = content
                    self._clipboard_queue.put(
                        (content, self.extract_tiktok_url(content), at_startup)
                    )
            except Exception as e:
                print(f"Clipboard monitoring error: {e}")
            self._clipboard_stop.wait(interval)

    def _is_busy(self):
        """True while a download runs or the video info of the current link is loading"""
        if self._downloading:
            return True
        if self._fetching:
            # Watchdog: a fetch that never reports back must not block the monitor forever
            if time.time() - self._fetch_started > 90:
                self.logger.warning("Video info fetch timed out, releasing the busy flag")
                self._fetching = False
                return False
            return True
        return False

    def _process_clipboard_queue(self):
        """Main thread: consume clipboard events produced by the polling thread."""
        if not self.clipboard_monitor_enabled:
            return

        try:
            latest = None
            while True:
                try:
                    latest = self._clipboard_queue.get_nowait()
                except queue.Empty:
                    break

            if latest is not None:
                content, url, at_startup = latest
                self.last_clipboard_content = content
                if url:
                    current_url = self.url_var.get().strip()
                    if not current_url or current_url != url:
                        if self._auto_download_enabled and self._is_busy():
                            # Don't overwrite the URL box mid-download: queue the link
                            if url not in self._auto_queue:
                                self._auto_queue.append(url)
                                self.status_var.set(f"Queued for auto download ({len(self._auto_queue)} waiting)")
                        else:
                            self.auto_paste_url(url, auto_start=not at_startup)

            # Links queued while busy are started as soon as the app is idle again,
            # not only when a download happens to finish.
            if self._auto_download_enabled and self._auto_queue and not self._is_busy():
                self.auto_paste_url(self._auto_queue.popleft())
        except Exception as e:
            print(f"Clipboard monitoring error: {e}")
            self.logger.error(f"Clipboard monitoring error: {e}")

        try:
            self.root.after(self.clipboard_check_interval, self._process_clipboard_queue)
        except tk.TclError:
            pass  # window already destroyed

    def auto_paste_url(self, url, auto_start=True):
        try:
            self.url_var.set(url)
            self.on_url_change()
            self.status_var.set(f"TikTok links detected")
            if auto_start and self._auto_download_enabled and self._fetching:
                # Start downloading once the video name has been fetched
                self._auto_pending_token = self._fetch_token
            self.logger.info(f"Automatically paste TikTok link: {url}")
            print(f"✅ Automatically paste TikTok link: {url}")
        except Exception as e:
            self.logger.error(f"Automatically paste failed: {str(e)}")
            print(f"❎ Automatically paste failed: {str(e)}")

    def create_left_column(self, parent):
        """Create left column with main controls"""
        left_frame = ctk.CTkFrame(parent, corner_radius=15, fg_color="#F8F9FA", width=390)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))
        left_frame.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            left_frame, 
            text="TTD: TikTok videos Downloader",
            font=ctk.CTkFont(size=20, weight="bold")
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
        
        # Engine + Quality share one row (half width each)
        self.create_engine_quality_section(left_frame)

        # Video Name Input
        self.create_video_name_section(left_frame)
        
        # Output Directory
        self.create_output_section(left_frame)

        # Auto Download checkbox + Update Libraries
        self.create_options_section(left_frame)
        
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
    def extract_tiktok_url(text):
        """
        Return the first TikTok link found in text, or None.
        TikTok's "Share" often copies extra text around the link
        (e.g. "Check out this video https://vm.tiktok.com/xxx/ #tiktok").
        """
        if not text or not isinstance(text, str):
            return None
        text = text.strip()
        # ASCII-only URL characters, so CJK punctuation after the link is not swallowed
        for m in re.finditer(r"https?://[A-Za-z0-9\-._~:/?#\[\]@!$&()*+,;=%]+", text, re.IGNORECASE):
            candidate = m.group(0).rstrip(".,;:!?)]")
            if HikariTikTokDownloader.is_tiktok_url(candidate):
                return candidate
        return None

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

    def create_engine_quality_section(self, parent):
        """Create Download Engine and Quality selectors side by side (half width each)"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 15))
        row.grid_columnconfigure(0, weight=1, uniform="eq_q")
        row.grid_columnconfigure(1, weight=1, uniform="eq_q")

        def build_cell(column, label_text, variable, values, info_command):
            cell = ctk.CTkFrame(row, fg_color="transparent")
            cell.grid(row=0, column=column, sticky="ew",
                      padx=(0, 8) if column == 0 else (8, 0))

            label = ctk.CTkLabel(cell, text=label_text, font=ctk.CTkFont(size=14, weight="bold"))
            label.pack(anchor="w")

            control_frame = ctk.CTkFrame(cell, fg_color="transparent")
            control_frame.pack(fill="x", pady=(5, 0))

            combo = ctk.CTkComboBox(
                control_frame,
                variable=variable,
                values=values,
                width=80,
                height=30,
                corner_radius=8,
                state="readonly"
            )
            combo.pack(side="left", fill="x", expand=True)

            info_btn = ctk.CTkButton(
                control_frame,
                text="ℹ️",
                width=30,
                height=30,
                corner_radius=15,
                command=info_command
            )
            info_btn.pack(side="right", padx=(5, 0))
            return combo

        self.engine_combo = build_cell(
            0, "Download Engine:", self.engine_var, ["yt-dlp"], self.show_engine_info
        )
        self.quality_combo = build_cell(
            1, "Quality:", self.quality_var, ["best"], self.show_quality_info
        )

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
        if self._in_name_change:
            return
        self._in_name_change = True
        try:
            content = self.video_name_textbox.get("1.0", "end-1c")
            self.video_name_var.set(content)
            # Reset the modified flag so the event triggers again on next edit
            self.video_name_textbox.edit_modified(False)
        finally:
            self._in_name_change = False

    # Button colours (iOS system palette, like the rest of the UI). Every button has its own
    # hue so it can be told apart at a glance; red is kept for "off / forbidden" only.
    #                    (normal,    hover)
    DOWNLOAD_COLOR = ("#007AFF", "#0056CC")   # blue   - main action
    HISTORY_COLOR = ("#AF52DE", "#8944AB")    # purple - browse past downloads
    UPDATE_COLOR = ("#30B0C7", "#258FA3")     # teal   - maintenance
    AUTO_ON_COLOR = ("#34C759", "#28A745")    # green  - auto download is on
    AUTO_OFF_COLOR = ("#FF3B30", "#D93025")   # red    - auto download is off

    def create_options_section(self, parent):
        """Auto Download toggle button and Update Libraries button, side by side"""
        options_frame = ctk.CTkFrame(parent, fg_color="transparent")
        options_frame.pack(fill="x", padx=20, pady=(0, 15))
        # "Auto Download Disabled" is the longest label, so it gets the wider column
        options_frame.grid_columnconfigure(0, weight=1, uniform="btn")
        options_frame.grid_columnconfigure(1, weight=1, uniform="btn")

        # Auto Download toggle: same shape/size/font as Update Libraries
        self.auto_download_btn = ctk.CTkButton(
            options_frame,
            text="",
            width=60,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white",
            command=self.on_auto_download_toggle
        )
        self.auto_download_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self._refresh_auto_download_button()

        # Update libraries button
        self.update_btn = ctk.CTkButton(
            options_frame,
            text="Update Libraries",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=60,
            fg_color=self.UPDATE_COLOR[0],
            hover_color=self.UPDATE_COLOR[1],
            text_color="white",
            command=self.update_libraries
        )
        self.update_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def _refresh_auto_download_button(self):
        """Blue 'Enabled' / red 'Disabled' look of the Auto Download button"""
        if self.auto_download_var.get():
            fg, hover = self.AUTO_ON_COLOR
            text = "Auto Download Enabled"
        else:
            fg, hover = self.AUTO_OFF_COLOR
            text = "Auto Download Disabled"
        self.auto_download_btn.configure(text=text, fg_color=fg, hover_color=hover)

    def on_auto_download_toggle(self):
        """Button handler: takes effect immediately and is remembered after restart"""
        enabled = not bool(self.auto_download_var.get())
        self.auto_download_var.set(enabled)
        self._auto_download_enabled = enabled
        if not enabled:
            self._auto_queue.clear()
            self._auto_pending_token = None
        self._refresh_auto_download_button()
        self.save_settings()
        self.status_var.set("Auto download enabled" if enabled else "Auto download disabled")
        self.logger.info(f"Auto download {'enabled' if enabled else 'disabled'}")

    def create_output_section(self, parent):
        """Create output directory section: full-width path box, buttons on the next row"""
        output_frame = ctk.CTkFrame(parent, fg_color="transparent")
        output_frame.pack(fill="x", padx=20, pady=(0, 26))
        
        output_label = ctk.CTkLabel(output_frame, text="Output Folder:", font=ctk.CTkFont(size=14, weight="bold"))
        output_label.pack(anchor="w")
        
        # Path box: same width as the Video Name box above
        self.output_entry = ctk.CTkEntry(
            output_frame,
            textvariable=self.output_dir,
            height=30,
            corner_radius=8
        )
        self.output_entry.pack(fill="x", pady=(5, 0))
        
        # Open / Browse / Default on their own row, evenly spread over the same width
        button_row = ctk.CTkFrame(output_frame, fg_color="transparent")
        button_row.pack(fill="x", pady=(8, 0))
        for col in range(3):
            button_row.grid_columnconfigure(col, weight=1, uniform="out_btn")

        buttons = (
            ("Open", self.open_output_folder),
            ("Browse", self.browse_output_folder),
            ("Default", self.set_default_folder),
        )
        for col, (text, command) in enumerate(buttons):
            ctk.CTkButton(
                button_row,
                text=text,
                width=60,
                height=30,
                corner_radius=8,
                command=command
            ).grid(row=0, column=col, sticky="ew",
                   padx=(0 if col == 0 else 4, 0 if col == 2 else 4))
        
    def create_download_section(self, parent):
        """Create download button section"""
        download_frame = ctk.CTkFrame(parent, fg_color="transparent")
        download_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Button container for side-by-side buttons
        button_container = ctk.CTkFrame(download_frame, fg_color="transparent")
        button_container.pack(fill="x", pady=(0, 5))
        button_container.grid_columnconfigure(0, weight=1, uniform="btn")
        button_container.grid_columnconfigure(1, weight=1, uniform="btn")

        # Main download button
        self.download_btn = ctk.CTkButton(
            button_container,
            text="Download Content",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.DOWNLOAD_COLOR[0],
            hover_color=self.DOWNLOAD_COLOR[1],
            text_color="white",  # White text color
            text_color_disabled="white",  # White text when disabled
            command=self.start_download
        )
        self.download_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Download History button
        self.history_btn = ctk.CTkButton(
            button_container,
            text="Download History",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.HISTORY_COLOR[0],
            hover_color=self.HISTORY_COLOR[1],
            text_color="white",
            command=self.show_download_history
        )
        self.history_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))
    
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
            text="Original - Gary19gts (Oct 2025)\nTTD - i0Ek3 (Nov 2025)\n",
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
        raw = self.url_var.get().strip()
        url = self.extract_tiktok_url(raw) or raw

        # Pasted share text (link + extra words): keep only the link
        if url != raw and self.is_tiktok_url(url):
            self.url_var.set(url)

        # KeyRelease fires for every key (Ctrl, arrows...). Don't refetch / wipe the
        # name if nothing changed, unless the previous fetch ended with no name.
        if url and url == self._current_url:
            if self._fetching or self.video_name_textbox.get("1.0", "end-1c").strip():
                return
        self._current_url = url

        # Invalidate any in-flight fetch for a previous URL
        self._fetch_token += 1
        token = self._fetch_token
        self._fetching = False

        # Clear the previous video name
        self.video_name_textbox.delete("1.0", "end")
        self.video_name_var.set("")

        if url:
            if self.is_tiktok_url(url):
                self.status_indicator.set_status("success", "Content detected")
                self.logger.info(f"Valid URL detected: {url}")

                # Fetch video info in a separate thread to avoid blocking UI
                self._fetching = True
                self._fetch_started = time.time()
                info_thread = threading.Thread(
                    target=self._fetch_video_info,
                    args=(url, token),
                    daemon=True
                )
                info_thread.start()
            else:
                self.status_indicator.set_status("error", "No content detected")
                self.logger.warning(f"Invalid URL format")
        else:
            self.status_indicator.set_status("error", "No content detected")

    # Fetch video metadata
    def _fetch_video_info(self, url, token=None):
        """
        Fetch video metadata using yt-dlp to auto-fill the video name.
        This method should be called from a thread to avoid freezing the UI.
        """
        if not url:
            return

        def ui(func):
            try:
                self.root.after(0, func)
            except Exception:
                pass  # window closed

        self.logger.info(f"Fetching video info for URL: {url}")

        current_engine_name = self.engine_var.get()
        current_engine = self.engines.get(current_engine_name)

        if current_engine_name != 'yt-dlp' or not hasattr(current_engine, 'DEFAULT_FILENAME_TEMPLATE'):
            self.logger.warning(f"Cannot fetch custom filename template for engine: {current_engine_name}")
            ui(lambda: self._update_video_name_ui("", token))
            return

        filename_template = current_engine.DEFAULT_FILENAME_TEMPLATE

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'noplaylist': True,
            'socket_timeout': 15,
        }

        max_attempts = 3
        last_error = None
        for attempt in range(1, max_attempts + 1):
            # Stop early if the URL has changed meanwhile
            if token is not None and token != self._fetch_token:
                return
            try:
                info = current_engine.extract_info(url)

                if info and info.get('entries'):
                    entries = [e for e in info['entries'] if e]
                    info = entries[0] if entries else None
                if not info:
                    raise ValueError("yt-dlp returned no info")

                # Keys may exist with a None value, so use "or" instead of get() defaults
                uploader = info.get('uploader') or info.get('uploader_id') or 'UnknownUploader'
                channel = info.get('channel') or uploader or 'UnknownChannel'
                title = (info.get('title') or info.get('description')
                         or info.get('id') or 'UnknownTitle')

                try:
                    video_name = filename_template % {
                        'channel': channel,
                        'uploader': uploader,
                        'title': title,
                        'id': info.get('id') or '',
                    }
                except (KeyError, TypeError, ValueError):
                    video_name = f"{uploader} - {title}"

                video_name = re.sub(r'\s+', ' ', video_name).strip()
                safe_video_name_for_ui = re.sub(r'[\\/*?:"<>|]', "", video_name)
                if not safe_video_name_for_ui:
                    raise ValueError("Empty video name")

                ui(lambda: self._update_video_name_ui(safe_video_name_for_ui, token))
                return

            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"Fetching video info failed (attempt {attempt}/{max_attempts}): {e}"
                )
                if attempt < max_attempts:
                    time.sleep(attempt)  # 1s, 2s back-off

        self.logger.error(f"Failed to fetch video info: {last_error}")
        ui(lambda: self._update_video_name_ui("", token))

    def _update_video_name_ui(self, video_name, token=None):
        """
        Safely update the video name input field (runs on the main thread).
        Results from outdated fetches (URL changed in the meantime) are ignored.
        """
        if token is not None and token != self._fetch_token:
            return

        self._fetching = False
        self.video_name_textbox.delete("1.0", "end")
        if video_name:
            self.video_name_textbox.insert("end", video_name)
            self.status_indicator.set_status("success", "Video info loaded")
        else:
            self.status_indicator.set_status("error", "No video info available")

        # Auto download: the link was auto-pasted and its info is ready (or unavailable
        # - the engine then falls back to its default file name)
        if (token is not None and token == self._auto_pending_token
                and self._auto_download_enabled):
            self._auto_pending_token = None
            self.status_var.set("Auto download started")
            self.start_download(auto=True)

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
            print(f"Could not load settings: {e}")
        return {}
    
    def save_settings(self):
        """Save current settings to JSON file"""
        try:
            settings = {
                "last_output_dir": self.output_dir.get(),
                "engine": self.engine_var.get(),
                "quality": self.quality_var.get(),
                "auto_download": bool(self.auto_download_var.get())
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            self.logger.debug("Settings saved successfully")
        except Exception as e:
            self.logger.warning(f"Could not save settings: {e}")
    
    def load_download_history(self):
        """Load download history from JSON file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return self._normalize_history(json.load(f))
        except Exception as e:
            self.logger.warning(f"Could not load download history: {e}")
        return []

    @staticmethod
    def _normalize_history(history):
        """
        Make sure every record has a unique integer id (newest = largest).
        Repairs files written by the old code, where all ids became 101.
        """
        if not isinstance(history, list):
            return []
        history = [r for r in history if isinstance(r, dict) and r.get("url")]
        ids = [r.get("id") for r in history]
        valid = all(isinstance(i, int) for i in ids) and len(set(ids)) == len(ids)
        if not valid:
            total = len(history)
            for idx, record in enumerate(history):  # history is newest first
                record["id"] = total - idx
        return history

    def save_download_history(self, history):
        """Save download history to JSON file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            self.logger.debug("Download history saved successfully")
        except Exception as e:
            self.logger.warning(f"Could not save download history: {e}")

    def add_to_history(self, url):
        """Add a download record to history"""
        history = self.load_download_history()
    
        # Create new record
        # Use max(id) + 1 instead of len(history) + 1: the list is capped at 100
        # records, so len()+1 would always be 101 once the cap is reached.
        next_id = max((r.get("id", 0) for r in history), default=0) + 1
        record = {
            "id": next_id,
            "url": url,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
        # Add to history (most recent first)
        history.insert(0, record)
    
        # No cap: the history window is paginated, so keep every record
        self.save_download_history(history)
        self.logger.info(f"Added to download history: {url}")

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
    
    def start_download(self, auto=False):
        """Start download process (auto=True when triggered by Auto Download)"""
        if self._downloading:
            return

        url = self.url_var.get().strip()
        # Store URL for history recording
        self.last_download_url = url

        def fail(title, message):
            # Auto mode must never block on a dialog before the next queued link
            if auto:
                self.status_var.set(message)
                self.logger.warning(f"Auto download skipped: {message}")
                self._schedule_next_auto()
            else:
                messagebox.showerror(title, message)

        if not url:
            fail("Error", "Please enter a TikTok URL")
            return
        
        # Validate URL
        is_valid, message = self.validator.is_valid_tiktok_url(url)
        if not is_valid:
            fail("Invalid URL", message)
            return
        
        # Check output directory
        output_path = self.output_dir.get()
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
            except Exception as e:
                fail("Error", f"Could not create output directory: {e}")
                return
        
        # Disable download button
        self._downloading = True
        self._download_is_auto = auto
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

        if auto:
            self.show_auto_download_toast(custom_video_name or url)
    
    def show_auto_download_toast(self, detail="", duration_ms=3000):
        """Small non-blocking popup telling the user an automatic download has started.
        It closes itself after duration_ms (3 seconds)."""
        try:
            toast = ctk.CTkToplevel(self.root)
            toast.title("Auto Download")
            toast.resizable(False, False)
            toast.configure(fg_color="white")
            toast.transient(self.root)
            try:
                toast.attributes("-topmost", True)
            except Exception:
                pass

            ctk.CTkLabel(
                toast,
                text="⬇️  Auto downloading...",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#1C1C1E"
            ).pack(padx=30, pady=(22, 4))

            if detail:
                shown = detail if len(detail) <= 60 else detail[:57] + "..."
                ctk.CTkLabel(
                    toast,
                    text=shown,
                    font=ctk.CTkFont(size=12),
                    text_color="#666666",
                    wraplength=320
                ).pack(padx=30, pady=(0, 6))

            ctk.CTkLabel(
                toast,
                text="This window closes automatically.",
                font=ctk.CTkFont(size=11),
                text_color="#999999"
            ).pack(padx=30, pady=(0, 20))

            # Center over the main window
            toast.update_idletasks()
            w, h = toast.winfo_reqwidth(), toast.winfo_reqheight()
            x = self.root.winfo_x() + (self.root.winfo_width() - w) // 2
            y = self.root.winfo_y() + (self.root.winfo_height() - h) // 2
            toast.geometry(f"{w}x{h}+{max(x, 0)}+{max(y, 0)}")
            toast.lift()

            def close():
                try:
                    if toast.winfo_exists():
                        toast.destroy()
                except Exception:
                    pass

            self.root.after(duration_ms, close)
        except Exception as e:
            self.logger.warning(f"Could not show auto download notice: {e}")
    
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
        self._downloading = False
        self.download_btn.configure(state="normal", text="Download Content")
        
        if success:
            self.progress_bar.set(1.0)
            self.status_var.set("Download completed!")
            self.logger.info("Download completed successfully")
            self.add_to_history(self.last_download_url)
            # Auto downloads finish silently (no modal dialog) so a batch of copied
            # links keeps flowing; manual downloads still show the dialog.
            if not self._download_is_auto:
                messagebox.showinfo("Success", message)
        else:
            self.progress_bar.set(0)
            self.status_var.set("Download failed")
            self.logger.error(f"Download failed: {message}")
            messagebox.showerror("Download Failed", message)

        self._schedule_next_auto()

    def _schedule_next_auto(self):
        """Continue with the next link copied while the previous one was busy"""
        if self._auto_download_enabled and self._auto_queue:
            self.root.after(300, self._start_next_queued)

    def _start_next_queued(self):
        if not self._auto_download_enabled or not self._auto_queue:
            return
        if self._is_busy():
            self.root.after(1000, self._start_next_queued)  # still busy, try again later
            return
        self.auto_paste_url(self._auto_queue.popleft())
    
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
        # Disable update button during process
        self.update_btn.configure(state="disabled", text="Updating...")
        self.status_var.set("Starting library update...")
        
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
                "curl_cffi",  # browser impersonation, required for TikTok
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
    
    HISTORY_PAGE_SIZE = 20

    def show_download_history(self):
        """Show download history window (paginated)"""
        history_window = ctk.CTkToplevel(self.root)
        history_window.title("Download History")
        history_window.geometry("700x560")
        history_window.configure(fg_color="white")

        # Make window modal
        history_window.transient(self.root)
        history_window.grab_set()

        # Main frame
        main_frame = ctk.CTkFrame(history_window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="📚 Download History",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#333333"
        )
        title_label.pack(pady=(10, 10))

        # Scrollable frame for history list
        scrollable_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="#F8F9FA",
            corner_radius=10,
            height=280
        )
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Pagination bar
        pager_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        pager_frame.pack(fill="x", padx=10, pady=(0, 10))

        def make_pager_btn(text, width, command):
            return ctk.CTkButton(
                pager_frame, text=text, width=width, height=30, corner_radius=8,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#007AFF", hover_color="#0056CC", text_color="white",
                text_color_disabled="#FFFFFF", command=command
            )

        first_btn = make_pager_btn("«", 40, lambda: goto_page(0))
        prev_btn = make_pager_btn("‹ Prev", 70, lambda: goto_page(state["page"] - 1))
        page_label = ctk.CTkLabel(
            pager_frame, text="", font=ctk.CTkFont(size=12), text_color="#666666"
        )
        next_btn = make_pager_btn("Next ›", 70, lambda: goto_page(state["page"] + 1))
        last_btn = make_pager_btn("»", 40, lambda: goto_page(10 ** 9))

        first_btn.pack(side="left", padx=(0, 5))
        prev_btn.pack(side="left")
        last_btn.pack(side="right", padx=(5, 0))
        next_btn.pack(side="right")
        page_label.pack(side="left", fill="x", expand=True)

        state = {"page": 0, "history": self.load_download_history()}
        page_size = self.HISTORY_PAGE_SIZE

        def total_pages():
            return max(1, (len(state["history"]) + page_size - 1) // page_size)

        def render_page():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            history = state["history"]
            pages = total_pages()
            state["page"] = min(max(state["page"], 0), pages - 1)
            page = state["page"]

            # Update pager state
            page_label.configure(
                text=f"Page {page + 1} / {pages}   ({len(history)} records)"
            )
            for btn, enabled in ((first_btn, page > 0), (prev_btn, page > 0),
                                 (next_btn, page < pages - 1), (last_btn, page < pages - 1)):
                btn.configure(state="normal" if enabled else "disabled")

            if not history:
                ctk.CTkLabel(
                    scrollable_frame,
                    text="No download history available",
                    font=ctk.CTkFont(size=14),
                    text_color="#999999"
                ).pack(pady=50)
                return

            # Header row
            header_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=(10, 5))
            ctk.CTkLabel(
                header_frame, text="#",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#666666", width=40
            ).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(
                header_frame, text="Download Time",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#666666", width=120
            ).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(
                header_frame, text="Download Link",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#666666"
            ).pack(side="left")

            separator = ctk.CTkFrame(scrollable_frame, height=1, fg_color="#E0E0E0")
            separator.pack(fill="x", padx=15, pady=(0, 10))

            # Rows of the current page only
            start = page * page_size
            for i, record in enumerate(history[start:start + page_size], start=start):
                item_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
                item_frame.pack(fill="x", padx=15, pady=2)

                ctk.CTkLabel(
                    item_frame, text=str(record.get("id", len(history) - i)),
                    font=ctk.CTkFont(size=11),
                    text_color="#666666", width=40
                ).pack(side="left", padx=(0, 10))

                ctk.CTkLabel(
                    item_frame, text=record.get("timestamp", ""),
                    font=ctk.CTkFont(size=11),
                    text_color="#666666", width=120
                ).pack(side="left", padx=(0, 10))

                url = record["url"]
                ctk.CTkButton(
                    item_frame,
                    text=url[:50] + "..." if len(url) > 50 else url,
                    font=ctk.CTkFont(size=10),
                    fg_color="transparent",
                    hover_color="#F0F0F0",
                    text_color="#007AFF",
                    anchor="w",
                    command=lambda u=url: self.copy_url_to_clipboard(u, history_window)
                ).pack(side="left", fill="x", expand=True)

            # Back to the top of the list after switching page
            try:
                scrollable_frame._parent_canvas.yview_moveto(0)
            except Exception:
                pass

        def goto_page(page):
            state["page"] = page
            render_page()

        def on_cleared():
            state["history"] = []
            state["page"] = 0
            render_page()

        render_page()

        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Clear history button
        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="Clear History",
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#007AFF",
            hover_color="#0056CC",
            text_color="white",
            command=lambda: self.clear_download_history(scrollable_frame, on_cleared)
        )
        clear_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Close button
        close_btn = ctk.CTkButton(
            buttons_frame,
            text="Close",
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#007AFF",
            hover_color="#0056CC",
            text_color="white",
            command=history_window.destroy
        )
        close_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

    def copy_url_to_clipboard(self, url, window):
        """Copy URL to clipboard and show confirmation"""
        try:
            pyperclip.copy(url)
            # Show temporary confirmation
            self.status_var.set("URL copied to clipboard!")
            window.after(2000, lambda: self.status_var.set("Ready"))
            self.logger.info(f"URL copied to clipboard: {url}")
        except Exception as e:
            self.logger.error(f"Failed to copy URL: {e}")
            messagebox.showerror("Error", "Failed to copy URL to clipboard")

    def clear_download_history(self, parent_frame, on_cleared=None):
        """Clear download history after confirmation"""
        result = messagebox.askyesno(
            "Clear History",
            "Are you sure you want to clear all download history? This action cannot be undone.",
            icon="warning"
        )
    
        if result:
            try:
                self.save_download_history([])
                if on_cleared:
                    # Paginated window re-renders itself (empty state + pager)
                    on_cleared()
                else:
                    for widget in parent_frame.winfo_children():
                        widget.destroy()
                    ctk.CTkLabel(
                        parent_frame,
                        text="No download history available",
                        font=ctk.CTkFont(size=14),
                        text_color="#999999"
                    ).pack(pady=50)
            
                self.status_var.set("Download history cleared")
                self.logger.info("Download history cleared")
            except Exception as e:
                self.logger.error(f"Failed to clear history: {e}")
                messagebox.showerror("Error", "Failed to clear download history")

    def on_closing(self):
        """Handle application closing"""
        self.clipboard_monitor_enabled = False
        self._clipboard_stop.set()
        self.save_settings()
        self.logger.info("TTD closed")
        self.root.destroy()

if __name__ == "__main__":
    app = HikariTikTokDownloader()
    app.run()
