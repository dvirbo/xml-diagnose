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


def get_date_input(prompt="Enter date (ddmmyyyy): "):
    """
    Prompt the user to input a date in the ddmmyyyy format.
    Args:
        prompt (str): The message displayed to the user when asking for input. 
                      Defaults to "Enter date (ddmmyyyy): ".
    Returns:
        str: A string representing the date entered by the user in ddmmyyyy format.
    Raises:
        ValueError: If the input is not exactly 8 digits or contains non-numeric characters.
    """
    while True:
        date_str = input(prompt).strip()
        
        # Check if input is exactly 8 digits
        if len(date_str) != 8 or not date_str.isdigit():
            print("Error: Date must be exactly 8 digits in ddmmyyyy format")
            continue
        
        return date_str

def main():
    """Main execution function."""
    # Setup logging first
    setup_logging()
    
    # Cleanup old logs
    cleanup_logs()
    
    # Get date from user
    target_date = get_date_input("Enter report date (ddmmyyyy): ") 
    #target_date = '13072025'
    logging.info(f"Processing reports for date: {target_date}")
    
    # Your main logic here
    logging.info("Starting pipeline process")
    
    config = load_config()
    input_dir = config.get('reports')
    pipeline = XMLDiagnosePipeline(input_dir, target_date)
    pipeline.run()
    


if __name__ == "__main__":
    main()
    
    
    
    '''
    filename meaning:
    
    ReportDate-?-UAR-ST-ReportNumber-ReportInstanceReference.FinR.XML
    
    the plan is:
    get the files that 

    '''