"""
utils/logger.py - Clean logging utility (no vulnerabilities)
"""
import logging
import sys
from datetime import datetime

def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

def log_event(logger, event_type, message, metadata=None):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "message": message,
    }
    if metadata:
        entry["metadata"] = metadata
    logger.info(str(entry))

def log_error(logger, error, context=None):
    logger.error(f"Error: {error}, Context: {context}")
