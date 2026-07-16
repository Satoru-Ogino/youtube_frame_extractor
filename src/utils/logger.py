import logging
import os
from datetime import datetime

class GUILogHandler(logging.Handler):
    """
    Custom logging handler that directs log messages to a GUI component via a callback.
    """
    def __init__(self, gui_callback=None):
        super().__init__()
        self.gui_callback = gui_callback

    def emit(self, record):
        log_entry = self.format(record)
        if self.gui_callback:
            # Safely invoke GUI callback (ensure thread safety in Tkinter by doing it via .after or similar if needed)
            self.gui_callback(log_entry)

# Global logger instance
logger = logging.getLogger("youtube_frame_extractor")
logger.setLevel(logging.DEBUG)

# Formatters
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] (%(filename)s:%(lineno)d) - %(message)s")

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Custom GUI Handler
gui_handler = GUILogHandler()
gui_handler.setLevel(logging.DEBUG)
gui_handler.setFormatter(formatter)
logger.addHandler(gui_handler)

def setup_file_logging(base_dir):
    """
    Initializes a file log handler under the given project directory.
    Uses UTF-8 to prevent encoding issues.
    """
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_path = os.path.join(log_dir, "extractor.log")
    
    # Avoid duplicate file handlers if configured multiple times
    for h in logger.handlers[:]:
        if isinstance(h, logging.FileHandler):
            logger.removeHandler(h)
            
    try:
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info(f"File logging initialized at: {log_path}")
    except Exception as e:
        logger.error(f"Failed to initialize file logging: {e}")

def set_gui_callback(callback):
    """
    Sets the callback function for the GUI log handler to output logs to a text box.
    """
    gui_handler.gui_callback = callback
