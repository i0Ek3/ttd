"""
Custom UI components with modern design
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

class ModernButton(ctk.CTkButton):
    """Modern button with clean design"""
    def __init__(self, parent, **kwargs):
        # Default styling
        default_kwargs = {
            'corner_radius': 8,
            'height': 35,
            'font': ctk.CTkFont(size=13, weight="normal")
        }
        default_kwargs.update(kwargs)
        super().__init__(parent, **default_kwargs)

class InfoTooltip:
    """Tooltip for showing information"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        if self.tooltip:
            return
        
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            self.tooltip,
            text=self.text,
            background="#333333",
            foreground="white",
            relief="solid",
            borderwidth=1,
            font=("Arial", 10),
            wraplength=300,
            justify="left",
            padx=8,
            pady=6
        )
        label.pack()
    
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class ProgressBar(ctk.CTkProgressBar):
    """Modern progress bar"""
    def __init__(self, parent, **kwargs):
        default_kwargs = {
            'height': 8,
            'corner_radius': 4,
            'progress_color': "#FF0050"
        }
        default_kwargs.update(kwargs)
        super().__init__(parent, **default_kwargs)

class StatusIndicator(ctk.CTkFrame):
    """Status indicator with colored dot"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.status_dot = ctk.CTkLabel(
            self,
            text="●",
            font=ctk.CTkFont(size=16),
            text_color="#FF6B6B"  # Red by default
        )
        self.status_dot.pack(side="left", padx=(0, 5))
        
        self.status_text = ctk.CTkLabel(
            self,
            text="Not detected",
            font=ctk.CTkFont(size=12)
        )
        self.status_text.pack(side="left")
    
    def set_status(self, status, text):
        """Set status indicator"""
        colors = {
            "success": "#4CAF50",
            "warning": "#FF9800", 
            "error": "#FF6B6B",
            "info": "#2196F3"
        }
        
        self.status_dot.configure(text_color=colors.get(status, "#FF6B6B"))
        self.status_text.configure(text=text)