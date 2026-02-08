"""Main entry point for XML diagnose pipeline."""
import logging
import os
import sys
from utils.config_loader import load_config
from utils.logging_setup import setup_logging, cleanup_logs
from core.pipeline import XMLDiagnosePipeline


def validate_date_format(date_str):
    """Validate date string is in dd/mm/yyyy format."""
    if not date_str or not isinstance(date_str, str):
        return False
    parts = date_str.strip().split('/')
    if len(parts) != 3:
        return False
    try:
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        if not (1 <= day <= 31 and 1 <= month <= 12 and 1000 <= year <= 9999):
            return False
        return True
    except ValueError:
        return False


def date_ddmmyyyy_to_filter(date_str):
    """Convert dd/mm/yyyy to ddmmyyyy for XML filename filtering."""
    parts = date_str.strip().split('/')
    day, month, year = parts[0].zfill(2), parts[1].zfill(2), parts[2]
    return "{}{}{}".format(day, month, year)


def main():
    """Main execution function."""
    # Setup logging first
    setup_logging()
    
    # Cleanup old logs
    cleanup_logs()
    
    # Get date from command line argument (dd/mm/yyyy format, e.g. 01/01/2025)
    if len(sys.argv) < 2:
        print("Error: Date argument is required.")
        print("Usage: python3 main.py <dd/mm/yyyy>")
        print("Example: python3 main.py 01/01/2025")
        sys.exit(1)
    
    date_input = sys.argv[1].strip()
    
    # Validate date format
    if not validate_date_format(date_input):
        print("Error: Date must be in dd/mm/yyyy format (e.g., 01/01/2025)")
        sys.exit(1)
    
    # Convert to ddmmyyyy for XML filename filtering (filenames use 01012025-...)
    folder_date_name = date_ddmmyyyy_to_filter(date_input)
    logging.info("Processing reports for date: {} (filter: {})".format(date_input, folder_date_name))
    
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
    # Query filter is now integrated: The pipeline automatically queries the latest process
    # and filters XML files to only process reports matching those report_ids.
    
    '''
    filename meaning:
    ReportDate-?-UAR-ST-ReportNumber-ReportInstanceReference.FinR.XML
    '''
