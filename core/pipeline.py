"""Main pipeline for processing XML reports."""
import logging
from typing import List, Dict, Optional
from database.manager import DatabaseManager
from processors.xml_processor import XMLReportProcessor


logging.basicConfig(level=logging.INFO)


class ProcessingResult:
    """Data class to hold processing results (Python 3.6 compatible)"""
    def __init__(self, summary_reports=None, reports=None):
        self.summary_reports = summary_reports
        self.reports = reports


class XMLDiagnosePipeline:
    """Main pipeline for processing XML reports"""
    
    def __init__(self, input_directory: str, date_filter: str = None):
        self.input_directory = input_directory
        self.date_filter = date_filter
        self.xml_processor = XMLReportProcessor(input_directory, date_filter)
        self.db_manager = DatabaseManager()
    
    def run(self) -> ProcessingResult:
        """Execute the complete processing pipeline"""
        result = ProcessingResult()
        
        try:
            # Step 1: Process XML files
            result.reports = self.xml_processor.process_xml_files()
            
            # Step 2: Export reports to CSV
            #TODO:add a method the export the error reports to csv flle
            
            #TODO: add a method that send the csv to the Rashut via email
            
            # Step 3: Update database (includes report log, status tracking, and alerts)
            if self.db_manager.connect():
                # Convert to lists if they're dictionaries, or use as-is if already lists
                all_reports = result.reports if isinstance(result.reports, list) else [result.reports] if result.reports else []
                result.summary_reports = self.db_manager.update_reports(all_reports)
                # Note: Alert updates are now handled within the database update process
            else:
                logging.error("Skipping database update due to connection failure")
                return result
            
            logging.info("Pipeline execution completed successfully")
            
        except Exception as e:
            logging.error("Pipeline execution failed: {}".format(str(e)))
            raise
        
        finally:
            # Close database connection
            self.db_manager.close()
        
        return result

