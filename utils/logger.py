"""
Logging utilities for diagnostics
"""

import logging
import os
from datetime import datetime
from pathlib import Path

class Logger:
    """Application logger for diagnostics"""
    
    def __init__(self, log_file="ttd.log"):
        self.log_file = log_file
        self.setup_logger()
        self.logs = []  # Store logs in memory for UI display
    
    def setup_logger(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger("TTD")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(
            log_dir / self.log_file,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log(self, level, message):
        """Log message with specified level"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {level.upper()}: {message}"
        
        # Store in memory
        self.logs.append(log_entry)
        
        # Keep only last 100 logs in memory
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
        
        # Log to file
        if level.lower() == 'debug':
            self.logger.debug(message)
        elif level.lower() == 'info':
            self.logger.info(message)
        elif level.lower() == 'warning':
            self.logger.warning(message)
        elif level.lower() == 'error':
            self.logger.error(message)
        elif level.lower() == 'critical':
            self.logger.critical(message)
    
    def info(self, message):
        """Log info message"""
        self.log('info', message)
    
    def warning(self, message):
        """Log warning message"""
        self.log('warning', message)
    
    def error(self, message):
        """Log error message"""
        self.log('error', message)
    
    def debug(self, message):
        """Log debug message"""
        self.log('debug', message)
    
    def get_recent_logs(self, count=20):
        """Get recent log entries"""
        return self.logs[-count:] if self.logs else []
    
    def clear_logs(self):
        """Clear in-memory logs"""
        self.logs.clear()
    
    def get_log_file_path(self):
        """Get path to log file"""
        return Path("logs") / self.log_file