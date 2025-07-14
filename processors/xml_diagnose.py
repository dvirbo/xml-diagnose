import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from api.alert_updater import AlertUpdater
from database.db_manager import DatabaseManager
from processors.xml_processor import XMLReportProcessor


logging.basicConfig(level=logging.INFO)

@dataclass
class ProcessingResult:
    """Data class to hold processing results"""
    error_csv: Optional[str] = None
    valid_csv: Optional[str] = None
    summary_report: List[Dict] = None
    error_reports: List[Dict] = None
    valid_reports: List[Dict] = None


class XMLDiagnosePipeline:
    """Main pipeline for processing XML reports"""
    
    def __init__(self, input_directory: str):
        self.input_directory = input_directory
        self.xml_processor = XMLReportProcessor(input_directory)
        self.db_manager = DatabaseManager()
        self.alert_updater = AlertUpdater()
    
    def run(self) -> ProcessingResult:
        """Execute the complete processing pipeline"""
        result = ProcessingResult()
        
        try:
            # Step 1: Process XML files
            result.error_reports, result.valid_reports = self.xml_processor.process_xml_files()
            
            # Step 2: Export reports to CSV
            result.error_csv, result.valid_csv = self.xml_processor.export_reports(
                result.error_reports, result.valid_reports
            )
            
            # Step 3: Update database
            if self.db_manager.connect():
                result.summary_report = self.db_manager.update_reports(result.valid_reports, result.error_reports)
            else:
                logging.error("Skipping database update due to connection failure")
                return result
            
            # Step 4: Update alerts
            if self.alert_updater.initialize_session():
                self.alert_updater.update_alerts(result.summary_report)
            else:
                logging.error("Skipping alert updates due to session failure")
            
            logging.info("Pipeline execution completed successfully")
            
        except Exception as e:
            logging.error(f"Pipeline execution failed: {str(e)}")
            raise
        
        finally:
            # Close database connection
            self.db_manager.close()
        
        return result