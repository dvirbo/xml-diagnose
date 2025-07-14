import os
import logging
from typing import List, Tuple
from processors.report_xml_classifier_v2 import parse_xml_files,classify_reports_by_status,export_reports_to_csv

class XMLReportProcessor:
    """Handles XML report parsing and classification"""
    
    def __init__(self, directory: str):
        self.directory = directory
        self.export_directory = os.path.join(directory, "exported_reports")
    
    def process_xml_files(self) -> Tuple[List, List]:
        """Parse and classify XML files"""
        logging.info("Starting XML file processing...")
        
        first_responses, final_responses = parse_xml_files(self.directory)
        
        # Add debugging logs
        logging.info(f"Parsed {len(first_responses) if first_responses else 0} first responses")
        logging.info(f"Parsed {len(final_responses) if final_responses else 0} final responses")
        
        # Handle potential None return from classify_reports_by_status
        error_reports, valid_reports = classify_reports_by_status(first_responses, final_responses)
        
        logging.info(f"Classification complete: {len(error_reports)} errors, {len(valid_reports)} valid")
        
        return error_reports, valid_reports
    
    def export_reports(self, error_reports: List, valid_reports: List) -> Tuple[str, str]:
        """Export reports to CSV files"""
        logging.info("Exporting reports to CSV...")
        
        error_csv, valid_csv = export_reports_to_csv(
            error_reports, 
            valid_reports, 
            output_directory=self.export_directory
        )
        
        logging.info(f"Error reports saved to: {error_csv}")
        logging.info(f"Valid reports saved to: {valid_csv}")
        
        return error_csv, valid_csv