import logging
from logging.handlers import TimedRotatingFileHandler
import os
import json
from datetime import datetime
from processors.xml_diagnose import XMLDiagnosePipeline


def load_config():
    """Load configuration from config.json file."""
    with open('config.json', 'r') as config_file:
        return json.load(config_file)


def setup_logging():
    """Setup logging configuration."""
    config = load_config()
    LOG_DIR = config.get('log_directory', 'logs')
    
    # Ensure log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Use base filename, let TimedRotatingFileHandler handle the date
    log_file = os.path.join(LOG_DIR, 'PipelineProcess.log')
    
    # Configure logging
    handler = TimedRotatingFileHandler(
        log_file, when='midnight', interval=1, backupCount=0, encoding='utf-8'
    )
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
    RETENTION_DAYS = config.get('retention_days', 90)
    
    now = datetime.now()
    for filename in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, filename)
        if os.path.isfile(file_path):
            file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if (now - file_creation_time).days > RETENTION_DAYS:
                os.remove(file_path)
                logging.info(f"Removed old log file: {filename}")


def main():
    """Main execution function."""
    # Setup logging first
    setup_logging()
    
    # Cleanup old logs
    cleanup_logs()
    
    # Your main logic here
    logging.info("Starting pipeline process")
    
    config = load_config()
    input_dir = config.get('reports')
    pipeline = XMLDiagnosePipeline(input_dir)
    pipeline.run()
    


if __name__ == "__main__":
    main()