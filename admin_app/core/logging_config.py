"""
DASAS Logging Configuration Module
===================================
Provides comprehensive logging setup for the DASAS Admin Dashboard.

Author: DASAS Team
Version: 1.0.0
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import threading

# Handle relative imports for both direct and package usage
try:
    from .config import settings
except ImportError:
    from core.config import settings


class DASASLogger:
    """
    Custom logger class for DASAS applications.
    
    Provides structured logging with file and console output,
    thread-safe operation, and configurable log levels.
    """
    
    _instance: Optional["DASASLogger"] = None
    _lock: threading.Lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern implementation"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Initialize the logger"""
        if self._initialized:
            return
        
        self._setup_logger()
        self._initialized = True
    
    def _setup_logger(self):
        """Set up the logger with configuration from settings"""
        self.logger = logging.getLogger("DASAS")
        
        # Set log level from configuration
        try:
            log_level = settings.monitoring.log_level
        except AttributeError:
            log_level = "INFO"
        
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Create logs directory if it doesn't exist
        log_path = Path("./logs")
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Log file path with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_path / f"dasas_{timestamp}.log"
        
        # File handler with rotation
        self._setup_file_handler(log_file)
        
        # Console handler
        self._setup_console_handler()
        
        # Add instance reference
        self.logger.dasas_instance = self
    
    def _setup_file_handler(self, log_file: Path):
        """Set up file handler for logging"""
        try:
            from logging.handlers import RotatingFileHandler
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10485760,  # 10MB
                backupCount=5,
                encoding="utf-8"
            )
            
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
            )
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.current_log_file = log_file
            
        except ImportError:
            # Fallback to basic file handler
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _setup_console_handler(self):
        """Set up console handler for logging"""
        console_handler = logging.StreamHandler(sys.stdout)
        
        formatter = logging.Formatter(
            "%(levelname)s: %(message)s"
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance"""
        return self.logger
    
    def set_level(self, level: str):
        """Set the log level dynamically"""
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    def log_metric(self, name: str, value: float, tags: dict = None):
        """
        Log a metric value.
        
        Args:
            name: Name of the metric
            value: Value to log
            tags: Optional tags for categorization
        """
        self.logger.info(
            f"METRIC: {name}={value} "
            f"tags={tags or {}}"
        )
    
    def log_event(self, event_type: str, event_data: dict):
        """
        Log a structured event.
        
        Args:
            event_type: Type of the event
            event_data: Event data dictionary
        """
        self.logger.info(
            f"EVENT: type={event_type} data={event_data}"
        )
    
    def log_error(self, error: Exception, context: dict = None):
        """
        Log an error with optional context.
        
        Args:
            error: Exception to log
            context: Optional context information
        """
        self.logger.error(
            f"ERROR: {str(error)}",
            exc_info=True,
            extra={"context": context or {}}
        )


# Global logger instance
logger = DASASLogger().get_logger()


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
    """
    # Reset existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create new handler
    handler = logging.StreamHandler(sys.stdout) if not log_file else logging.FileHandler(log_file)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))


class LogManager:
    """
    Manager class for handling log operations.
    
    Provides methods for reading, searching, and analyzing logs.
    """
    
    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = Path(log_dir)
    
    def get_log_files(self) -> list:
        """Get list of log files"""
        if not self.log_dir.exists():
            return []
        return list(self.log_dir.glob("*.log"))
    
    def read_logs(self, log_file: Path, lines: int = 100) -> list:
        """
        Read last N lines from a log file.
        
        Args:
            log_file: Path to log file
            lines: Number of lines to read
            
        Returns:
            List of log lines
        """
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                return f.readlines()[-lines:]
        except Exception as e:
            logger.error(f"Error reading log file: {e}")
            return []
    
    def search_logs(self, log_file: Path, pattern: str) -> list:
        """
        Search for pattern in log file.
        
        Args:
            log_file: Path to log file
            pattern: Search pattern
            
        Returns:
            List of matching lines
        """
        import re
        matches = []
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if re.search(pattern, line, re.IGNORECASE):
                        matches.append(line.strip())
        except Exception as e:
            logger.error(f"Error searching log file: {e}")
        return matches
    
    def clear_old_logs(self, days: int = 7):
        """
        Clear logs older than N days.
        
        Args:
            days: Number of days to retain logs
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        
        for log_file in self.get_log_files():
            if log_file.stat().st_mtime < cutoff.timestamp():
                try:
                    log_file.unlink()
                    logger.info(f"Deleted old log file: {log_file}")
                except Exception as e:
                    logger.error(f"Error deleting log file: {e}")
