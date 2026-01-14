"""Logging setup and cleanup utilities."""
import logging
import os
from datetime import datetime
from utils.config_loader import load_config


def setup_logging():
    """Setup logging configuration."""
    config = load_config()
    LOG_DIR = config.get('log_directory', 'logs')
    
    # Ensure log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Create date-specific log file name
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(LOG_DIR, 'PipelineProcess_{}.log'.format(today))
    
    # Configure logging with file handler
    handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # Clear any existing handlers and set up logging
    logging.getLogger().handlers.clear()
    logging.basicConfig(level=logging.INFO, handlers=[handler])
    
    # Test logging
    logging.info("Logging system initialized successfully")


def cleanup_logs():
    """Cleanup old log files based on retention policy."""
    config = load_config()
    LOG_DIR = config.get('log_directory', 'logs')
    RETENTION_DAYS = int(config.get('retention_days', 90))
    
    now = datetime.now()
    for filename in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, filename)
        if os.path.isfile(file_path):
            file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if (now - file_creation_time).days > RETENTION_DAYS:
                os.remove(file_path)
                logging.info("Removed old log file: {}".format(filename))

