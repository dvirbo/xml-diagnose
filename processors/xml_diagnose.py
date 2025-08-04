import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from api.alert_updater import AlertUpdater
from api.api_session import end_session
from database.db_manager import DatabaseManager
from processors.xml_processor import XMLReportProcessor


logging.basicConfig(level=logging.INFO)

@dataclass
class ProcessingResult:
    """Data class to hold processing results"""
    summary_reports: List[Dict] = None
    reports: List[Dict] = None



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
            result.reports = self.xml_processor.process_xml_files()
            
            # Step 2: Export reports to CSV
            #TODO:add a method the export the error reports to csv flle
            
            #TODO: add a method that send the csv to the Rashut via email
            
            # Step 3: Update database
            if self.db_manager.connect():
                # Convert to lists if they're dictionaries, or use as-is if already lists
                all_reports = result.reports if isinstance(result.reports, list) else [result.reports] if result.reports else []
                result.summary_reports = self.db_manager.update_reports(all_reports) #TODO: remove the comment when the db_manager is ready
            else:
                logging.error("Skipping database update due to connection failure")
                return result
            
            # Step 4: Update alerts
            if self.alert_updater.initialize_session():
                self.alert_updater.update_alerts(all_reports)
            else:
                logging.error("Skipping alert updates due to session failure")
            
            logging.info("Pipeline execution completed successfully")
            
        except Exception as e:
            logging.error(f"Pipeline execution failed: {str(e)}")
            raise
        
        finally:
            # Close database connection
            self.db_manager.close()
            #close session and logout ActOne
            end_session(self.alert_updater.session)

            
        
        return result
    
    #some test code