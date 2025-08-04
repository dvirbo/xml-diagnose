import pyodbc
import logging
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from database.config import SQL_QUERIES, DB_SETTINGS

@dataclass
class ReportUpdate:
    report_id: str
    alert_id: str
    status_divuah: str
    mispar_tkina: str
    received_date: str
    comments: str
    ErrorCode: Optional[int] = None  # Optional field for error code, can be None if not present

@dataclass
class ProcessedReport:
    """Data class to hold processed report information"""
    report_number: str
    report_data: Dict
    report_id: Optional[str]
    alert_id: Optional[str]
    sar_folder_name: Optional[str]
    first_response: Dict
    final_response: Dict
    status: Dict

class DatabaseUpdater:
    def __init__(self, connection: pyodbc.Connection):
        self.connection = connection
        self.cursor = connection.cursor()
                
    
    def _get_existing_reports_bulk(self, report_numbers: List[str]) -> Dict[str, Tuple[Optional[str], Optional[str], Optional[str]]]:
        """Get existing report and alert IDs from database in bulk."""
        try:
            if not report_numbers:
                return {}
            # Create placeholders for the IN clause
            placeholders = ','.join(['?' for _ in report_numbers])
            bulk_query = SQL_QUERIES['SELECT_REPORTS_BULK'].format(placeholders=placeholders)
            
            self.cursor.execute(bulk_query, report_numbers)
            rows = self.cursor.fetchall()
            
            # Create a mapping of report_id -> (report_id, alert_id, folder_name)
            result = {}
            for row in rows:
                report_id = row[0]  # report_id is the first column
                alert_id = row[1]   # alert_id is the second column
                folder_name = row[2] # Folder_name - need to sent as part of the csv file
                result[report_id] = (report_id, alert_id, folder_name)
            
            return result
            
        except Exception as e:
            logging.error(f"Error fetching bulk report info: {e}")
            return {report_number: (None, None, None) for report_number in report_numbers}

    def _parse_reports_input(self, reports: Union[Dict, List]) -> Tuple[List[str], List[Tuple[str, Dict]]]:
        """
        Parse the reports input and return report numbers and items.
        
        Args:
            reports: Can be:
                    - A dictionary with report numbers as keys
                    - A list containing a single dictionary with report numbers as keys
                    - A list of report numbers
            
        Returns:
            Tuple of (report_numbers, reports_items)
        """
        logging.debug(f"_parse_reports_input called with type: {type(reports)}")
        
        # Handle list containing a single dictionary
        if isinstance(reports, list) and len(reports) == 1 and isinstance(reports[0], dict):
            reports = reports[0]  # Extract the dictionary from the list
            logging.debug("Extracted dictionary from list")
        
        if isinstance(reports, dict):
            # Input is a dictionary with report numbers as keys
            report_numbers = list(reports.keys())
            reports_items = list(reports.items())
            logging.debug(f"Dict case - report_numbers: {report_numbers}")
            logging.debug(f"Dict case - reports_items count: {len(reports_items)}")
    
        # Ensure all report_numbers are strings
        report_numbers = [str(rn) for rn in report_numbers if rn is not None]
        logging.debug(f"Final report_numbers: {report_numbers}")
        logging.debug(f"Final reports_items count: {len(reports_items)}")
        
        return report_numbers, reports_items

    def _process_single_report(self, report_number: str, report_data: Dict, 
                              existing_reports: Dict) -> Optional[ProcessedReport]:
        """
        Process a single report and return processed data.
        
        Args:
            report_number: The report number
            report_data: The report data dictionary
            existing_reports: Dictionary of existing reports from database
            
        Returns:
            ProcessedReport object or None if processing failed
        """
        try:
            # Get existing report info
            existing_info = existing_reports.get(int(report_number), (None, None, None)) #TODO:check it
            report_id, alert_id, sar_folder_name = existing_info
            
            if not report_id or not alert_id:
                logging.warning(f"Report {report_number} not found in database")
                return None
            
            # Extract data from parsed report
            first_response = report_data.get('FirstResponse', {})
            final_response = report_data.get('FinalResponse', {})
            status = report_data.get('Status', {})
            
            return ProcessedReport(
                report_number=report_number,
                report_data=report_data,
                report_id=report_id,
                alert_id=alert_id,
                sar_folder_name=sar_folder_name,
                first_response=first_response,
                final_response=final_response,
                status=status
            )
            
        except Exception as e:
            logging.error(f"Error processing report {report_number}: {e}")
            return None

    def _prepare_report_log_update(self, processed_report: ProcessedReport) -> Tuple:
        """
        Prepare data for UPDATE_REPORT_LOG query.
        
        Args:
            processed_report: ProcessedReport object
            
        Returns:
            Tuple of data for UPDATE_REPORT_LOG
        """
        first_response = processed_report.first_response
        final_response = processed_report.final_response
        status = processed_report.status
        
        report_date = first_response.get('ReportDate', '') if first_response else ''
        first_response_valid = status.get('first_response_valid', False)
        final_response_valid = status.get('final_response_valid', False)
        received_date = first_response.get('ReportDate', '') if first_response else ''
        status_desc = status.get('status_category', '')
        
        # Handle mispar_tkina - only exists if final response is valid
        if final_response and final_response_valid:
            mispar_tkina = final_response.get('mispar_tkina', '')
        else:
            mispar_tkina = ''  # Empty string if report is not valid or no final response
        
        return (
            report_date,
            first_response_valid,
            final_response_valid,
            received_date,
            mispar_tkina,
            status_desc,
            processed_report.report_id  # WHERE clause parameter
        )

    def _prepare_status_tracking_insert(self, processed_report: ProcessedReport) -> Tuple:
        """
        Prepare data for INSERT_STATUS_TRACKING query.
        
        Args:
            processed_report: ProcessedReport object
            
        Returns:
            Tuple of data for INSERT_STATUS_TRACKING
        """
        first_response = processed_report.first_response
        final_response = processed_report.final_response
        status = processed_report.status
        
        update_date = first_response.get('ReportDate', '') if first_response else ''
        comments = final_response.get('ReportInstanceStatusReason', '') if final_response else ''
        status_desc = status.get('status_category', '')
        first_response_valid = status.get('first_response_valid', False)
        final_response_valid = status.get('final_response_valid', False)
        
        return (
            processed_report.report_id,
            processed_report.alert_id,
            update_date,
            status_desc,
            comments,
            first_response_valid,
            final_response_valid
        )

    def _execute_bulk_updates(self, updates_for_report_log: List[Tuple], 
                             updates_for_status_tracking: List[Tuple]) -> None:
        """
        Execute bulk database updates.
        
        Args:
            updates_for_report_log: List of tuples for UPDATE_REPORT_LOG
            updates_for_status_tracking: List of tuples for INSERT_STATUS_TRACKING
        """
        # Update IMP_REPORT_LOG
        if updates_for_report_log:
            try:
                self.cursor.executemany(SQL_QUERIES['UPDATE_REPORT_LOG'], updates_for_report_log)
                logging.info(f"Updated {len(updates_for_report_log)} records in IMP_REPORT_LOG")
            except Exception as e:
                logging.error(f"Error updating IMP_REPORT_LOG: {e}")
                raise
        
        # Insert into IMP_REPORT_STATUS_TRACKING
        if updates_for_status_tracking:
            try:
                self.cursor.executemany(SQL_QUERIES['INSERT_STATUS_TRACKING'], updates_for_status_tracking)
                logging.info(f"Inserted {len(updates_for_status_tracking)} records in IMP_REPORT_STATUS_TRACKING")
            except Exception as e:
                logging.error(f"Error inserting into IMP_REPORT_STATUS_TRACKING: {e}")
                raise

    def update_database_bulk(self, reports: Union[Dict, List]) -> None:
        """
        Updates the database with the provided reports using bulk operations.
        
        Args:
            reports: Dictionary of report data or list of reports
        """
        try:
            if not reports:
                logging.info("No reports to process")
                return
            
            logging.info(f"Starting bulk update for {len(reports)} reports")
            logging.debug(f"Input reports type: {type(reports)}")
            if isinstance(reports, dict):
                logging.debug(f"Report keys: {list(reports.keys())}")
            
            # Step 1: Parse input and get existing reports
            report_numbers, reports_items = self._parse_reports_input(reports)
            logging.info(f"Parsed {len(report_numbers)} report numbers: {report_numbers[:5]}...")  # Show first 5
            logging.info(f"Parsed {len(reports_items)} report items")
            
            existing_reports = self._get_existing_reports_bulk(report_numbers)
            logging.info(f"Found {len(existing_reports)} existing reports in database")


            for report_dict in reports:
                for report_number, report_data in report_dict.items():
                    report_num_int = int(report_number)
                    if report_num_int in existing_reports:
                        sam1_value = existing_reports[report_num_int][1]  # Extract 'SAM1-xxxx'
                        report_data['alert_id'] = sam1_value  # Add it to the report

            
            # Step 2: Process reports and prepare updates
            updates_for_report_log = []
            updates_for_status_tracking = []
            
            processed_count = 0
            missing_count = 0
            failed_count = 0
            
            for report_number, report_data in reports_items:
                logging.debug(f"Processing report {report_number}")
                
                processed_report = self._process_single_report(
                    report_number, report_data, existing_reports
                )
                
                if processed_report is None:
                    missing_count += 1
                    logging.debug(f"Report {report_number} not found in database or processing failed")
                    continue
                
                try:
                    # Prepare update data
                    report_log_update = self._prepare_report_log_update(processed_report)
                    status_tracking_insert = self._prepare_status_tracking_insert(processed_report)
                    
                    updates_for_report_log.append(report_log_update)
                    updates_for_status_tracking.append(status_tracking_insert)
                    
                    processed_count += 1
                    logging.debug(f"Successfully prepared updates for report {report_number}")
                    
                except Exception as e:
                    failed_count += 1
                    logging.error(f"Error preparing updates for report {report_number}: {e}")
            
            logging.info(f"Processed {processed_count} reports, {missing_count} missing from DB, {failed_count} failed")
            
            # Step 3: Execute bulk updates
            self._execute_bulk_updates(updates_for_report_log, updates_for_status_tracking)
            
            # Step 4: Commit the transaction
            self.connection.commit()
            logging.info(f"Database update completed successfully. Updated {processed_count} reports.")
            return reports
            
        except Exception as e:
            # Rollback on error
            self.connection.rollback()
            logging.error(f"Database update failed: {e}")
            raise

def update_db(connection: pyodbc.Connection, reports: Union[Dict, List]) -> str:
    """
    Updates the database with the provided reports using bulk operations.
    
    Args:
        connection: Database connection
        reports: Dictionary of report data or list of reports
        
    Returns:
        str: Summary of the updates made
    """
    updater = DatabaseUpdater(connection)
    return updater.update_database_bulk(reports)