"""Main pipeline for processing XML reports."""
import logging
from typing import List, Dict, Optional
from database.manager import DatabaseManager
from processors.xml_processor import XMLReportProcessor
from utils.config_loader import load_config
from utils.report_exporter import export_reports_to_csv


logging.basicConfig(level=logging.INFO)


class ProcessingResult:
    """Data class to hold processing results (Python 3.6 compatible)"""
    def __init__(self, summary_reports=None, reports=None):
        self.summary_reports = summary_reports
        self.reports = reports


class XMLDiagnosePipeline:
    """Main pipeline for processing XML reports"""
    
    def __init__(self, input_directory: str, date_filter: str = None, use_query_filter: bool = True):
        self.input_directory = input_directory
        self.date_filter = date_filter
        self.use_query_filter = use_query_filter
        self.db_manager = DatabaseManager()
        self.xml_processor = None  # Will be initialized after getting report_ids
    
    def run(self) -> ProcessingResult:
        """Execute the complete processing pipeline"""
        result = ProcessingResult()
        
        try:
            # Step 0: Get report_ids from latest process if query filter is enabled
            allowed_report_ids = None
            if self.use_query_filter:
                if not self.db_manager.connect():
                    logging.error("Failed to connect to database. Cannot filter by query results.")
                    logging.info("Continuing without query filter...")
                else:
                    try:
                        # Get report_ids from latest process
                        report_ids = self.db_manager.get_reports_from_latest_process()
                        if report_ids:
                            allowed_report_ids = set(report_ids)
                            logging.info("Using query filter: {} report_ids from latest process".format(len(allowed_report_ids)))
                        else:
                            logging.warning("No reports found from latest process. Processing all files.")
                    except Exception as e:
                        logging.error("Error getting reports from latest process: {}".format(e))
                        logging.info("Continuing without query filter...")
            
            # Step 1: Process XML files (with optional filtering by report_ids)
            self.xml_processor = XMLReportProcessor(self.input_directory, self.date_filter, allowed_report_ids)
            result.reports = self.xml_processor.process_xml_files()
            
            # Step 2: Update database with filtered results
            # This step updates IMP_REPORT_LOG, IMP_REPORT_STATUS_TRACKING, and actone.alerts tables
            # with the parsed and filtered report data from Step 1
            # Returns export rows (with SAR_FOLDER_NAME) for CSV export
            if not self.db_manager.connection:
                if not self.db_manager.connect():
                    logging.error("Skipping database update due to connection failure")
                    return result
            
            # Convert to lists if they're dictionaries, or use as-is if already lists
            all_reports = result.reports if isinstance(result.reports, list) else [result.reports] if result.reports else []
            result.summary_reports = self.db_manager.update_reports(all_reports)
            # Note: Alert updates are now handled within the database update process
            
            # Step 3: Export reports to CSV (requires SAR_FOLDER_NAME from DB update)
            export_rows = result.summary_reports if isinstance(result.summary_reports, list) else []
            if export_rows:
                config = load_config()
                export_dir = config.get('export_directory', '/var/Reports_To_Send')
                try:
                    export_reports_to_csv(export_rows, export_dir)
                except Exception as e:
                    logging.error("CSV export failed: {}".format(e))
                    # Continue - do not fail the pipeline for export errors
            else:
                logging.info("No reports to export, skipping CSV export")
            
            logging.info("Pipeline execution completed successfully")
            
        except Exception as e:
            logging.error("Pipeline execution failed: {}".format(str(e)))
            raise
        
        finally:
            # Close database connection
            self.db_manager.close()
        
        return result

