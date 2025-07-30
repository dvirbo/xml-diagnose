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
    
    # Create date-specific log file name
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(LOG_DIR, f'PipelineProcess_{today}.log')
    
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
    RETENTION_DAYS = config.get('retention_days', 90)
    
    now = datetime.now()
    for filename in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, filename)
        if os.path.isfile(file_path):
            file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if (now - file_creation_time).days > RETENTION_DAYS:
                os.remove(file_path)
                logging.info(f"Removed old log file: {filename}")


def get_date_input(prompt="Enter date (dd_mm_yyyy): "):
    """Get date input from user as string in dd_mm_yyyy format."""
    while True:
        date_str = input(prompt).strip()
        
        # Check if input is exactly 10 digits
        if len(date_str) != 10 or not date_str.isdigit():
            print("Error: Date must be exactly 10 digits in dd_mm_yyyy format")
            continue
        
        return date_str

def main():
    """Main execution function."""
    # Setup logging first
    setup_logging()
    
    # Cleanup old logs
    cleanup_logs()
    
    # Get date from user
    #target_date = get_date_input("Enter report date (ddmmyyyy): ") 
    folder_date_name= '13_07_2025'
    logging.info(f"Processing reports for date: {folder_date_name}")
    
    # Your main logic here
    logging.info("Starting pipeline process")
    
    config = load_config()
    input_dir = os.path.join(config.get('reports'), folder_date_name)
    pipeline = XMLDiagnosePipeline(input_dir)
    pipeline.run()
    


if __name__ == "__main__":
    main()
    
    
    
    '''
    filename meaning:
    
    ReportDate-?-UAR-ST-ReportNumber-ReportInstanceReference.FinR.XML
    

    fields that need to gets from IMP_REPORT_LOG table:
    
    ErrorCode

    '''