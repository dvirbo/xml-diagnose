import os
import logging
from typing import List, Tuple
from processors.xml_parser import link_responses, parse_xml_files

class XMLReportProcessor:
    """Handles XML report parsing and classification"""
    
    def __init__(self, directory: str, date_filter: str = None):
        self.directory = directory
        self.date_filter = date_filter
        self.export_directory = os.path.join(directory, "exported_reports")
    
    def process_xml_files(self) -> Tuple[List, List]:
        """Parse and classify XML files"""
        logging.info("Starting XML file processing...")
        if self.date_filter:
            logging.info("Filtering XML files by date prefix: {}".format(self.date_filter))
        
        first_responses, final_responses = parse_xml_files(self.directory, self.date_filter) 
        
        # Add debugging logs
        first_count = len(first_responses) if first_responses else 0
        final_count = len(final_responses) if final_responses else 0
        logging.info("Parsed {} first responses".format(first_count))
        logging.info("Parsed {} final responses".format(final_count))
        
        # Handle potential None return from classify_reports_by_status
        combined_reports = link_responses(first_responses, final_responses)
                
        return combined_reports
    

    