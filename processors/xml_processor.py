import os
import logging
from typing import List, Tuple
from processors.report_xml_classifier_v2 import link_responses, parse_xml_files

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
        combined_reports = link_responses(first_responses, final_responses)
                
        return combined_reports
    

    