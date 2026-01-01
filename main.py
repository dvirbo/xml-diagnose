"""Main entry point for XML diagnose pipeline."""
import logging
import os
from utils.config_loader import load_config
from utils.logging_setup import setup_logging, cleanup_logs
from core.pipeline import XMLDiagnosePipeline


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
    folder_date_name = '01_01_2025'
    logging.info("Processing reports for date: {}".format(folder_date_name))
    
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
    '''
