"""Main entry point for XML diagnose pipeline."""
import logging
import os
import sys
from utils.config_loader import load_config
from utils.logging_setup import setup_logging, cleanup_logs
from core.pipeline import XMLDiagnosePipeline


def validate_date_format(date_str):
    """Validate date string is in ddmmyyyy format."""
    if not date_str:
        return False
    if len(date_str) != 8 or not date_str.isdigit():
        return False
    return True


def main():
    """Main execution function."""
    # Setup logging first
    setup_logging()
    
    # Cleanup old logs
    cleanup_logs()
    
    # Get date from command line argument
    if len(sys.argv) < 2:
        print("Error: Date argument is required.")
        print("Usage: python3 main.py <ddmmyyyy>")
        print("Example: python3 main.py 01012025")
        sys.exit(1)
    
    folder_date_name = sys.argv[1].strip()
    
    # Validate date format
    if not validate_date_format(folder_date_name):
        print("Error: Date must be exactly 8 digits in ddmmyyyy format (e.g., 01012025)")
        sys.exit(1)
    
    logging.info("Processing reports for date: {}".format(folder_date_name))
    
    # Your main logic here
    logging.info("Starting pipeline process")
    
    config = load_config()
    # Input directory (contains FirstResponses/ and FinalResponses/ subfolders)
    # Input directory is relative to project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    input_dir_name = config.get('input_directory', 'Response_From_Rashut_05')
    input_dir = os.path.join(project_root, input_dir_name)
    pipeline = XMLDiagnosePipeline(input_dir, date_filter=folder_date_name)
    pipeline.run()


if __name__ == "__main__":
    main()
    #TODO: We need to add an SQL query (provided by Ornael) that retrieves all relevant report_id values. 
    #TODO: These IDs will then be passed to the process_xml_files function, which will use them to fetch and process all corresponding files.
    
    '''
    filename meaning:
    ReportDate-?-UAR-ST-ReportNumber-ReportInstanceReference.FinR.XML
    '''
