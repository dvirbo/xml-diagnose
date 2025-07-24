import os
import logging
import concurrent.futures
from typing import List, Tuple, Dict, Any
from processors.report_xml_classifier_optimized import (
    parse_xml_files_concurrent, 
    classify_reports_by_status,
    export_reports_to_csv_optimized
)


class XMLReportProcessorOptimized:
    """Optimized XML report processor with concurrent processing and improved performance"""
    
    def __init__(self, directory: str, target_date: str, max_workers: int = None):
        self.directory = directory
        self.input_date = target_date
        self.export_directory = os.path.join(directory, "exported_reports")
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        
        # Ensure export directory exists
        os.makedirs(self.export_directory, exist_ok=True)
    
    def process_xml_files(self, input_date: str) -> Tuple[List, List]:
        """Parse and classify XML files with concurrent processing"""
        logging.info(f"Starting optimized XML file processing with {self.max_workers} workers...")
        
        # Use concurrent parsing for better performance
        first_responses, final_responses = parse_xml_files_concurrent(
            self.directory, 
            self.input_date, 
            max_workers=self.max_workers
        )
        
        # Add debugging logs
        logging.info(f"Parsed {len(first_responses) if first_responses else 0} first responses")
        logging.info(f"Parsed {len(final_responses) if final_responses else 0} final responses")
        
        # Classify reports
        error_reports, valid_reports = classify_reports_by_status(first_responses, final_responses)
        
        logging.info(f"Classification complete: {len(error_reports)} errors, {len(valid_reports)} valid")
        
        # Clear intermediate data to free memory
        del first_responses, final_responses
        
        return error_reports, valid_reports
    
    def export_reports(self, error_reports: List, valid_reports: List) -> Tuple[str, str]:
        """Export reports to CSV files with optimized I/O"""
        logging.info("Exporting reports to CSV with optimized I/O...")
        
        error_csv, valid_csv = export_reports_to_csv_optimized(
            error_reports, 
            valid_reports, 
            output_directory=self.export_directory
        )
        
        logging.info(f"Error reports saved to: {error_csv}")
        logging.info(f"Valid reports saved to: {valid_csv}")
        
        return error_csv, valid_csv