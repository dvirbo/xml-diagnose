"""Database update operations."""
import cx_Oracle as oracledb
import logging
from typing import Dict, List, Tuple, Optional, Union
from database.queries import SQL_QUERIES, DB_SETTINGS


class ReportUpdate:
    """Data class to hold report update information (Python 3.6 compatible)"""
    def __init__(self, report_id, alert_id, status_divuah, mispar_tkina, received_date, comments, ErrorCode=None):
        self.report_id = report_id
        self.alert_id = alert_id
        self.status_divuah = status_divuah
        self.mispar_tkina = mispar_tkina
        self.received_date = received_date
        self.comments = comments
        self.ErrorCode = ErrorCode  # Optional field for error code, can be None if not present


class ProcessedReport:
    """Data class to hold processed report information (Python 3.6 compatible)"""
    def __init__(self, report_number, report_data, report_id, alert_id, sar_folder_name, first_response, final_response, status):
        self.report_number = report_number
        self.report_data = report_data
        self.report_id = report_id
        self.alert_id = alert_id
        self.sar_folder_name = sar_folder_name
        self.first_response = first_response
        self.final_response = final_response
        self.status = status


class DatabaseUpdater:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
                
    
    def _get_existing_reports_bulk(self, report_numbers: List[str]) -> Dict[str, Tuple[Optional[str], Optional[str], Optional[str]]]:
        """Get existing report and alert IDs from database in bulk."""
        try:
            if not report_numbers:
                return {}
            # Create placeholders for the IN clause - Oracle uses :1, :2, etc.
            placeholders = ','.join([':{}'.format(i+1) for i in range(len(report_numbers))])
            bulk_query = SQL_QUERIES['SELECT_REPORTS_BULK'].format(placeholders=placeholders)
            
            self.cursor.execute(bulk_query, report_numbers)
            rows = self.cursor.fetchall()
            
            # Create a mapping of report_id -> (report_id, alert_id, folder_name)
            result = {}
            for row in rows:
                report_id = row[0]  # report_id is the first column
                alert_id = row[1]   # alert_id is the second column
                folder_name = row[2] if len(row) > 2 else None  # SAR_folder_name - may be None
                result[report_id] = (report_id, alert_id, folder_name)
            
            return result
            
        except Exception as e:
            logging.error("Error fetching bulk report info: {}".format(e))
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
        logging.debug("_parse_reports_input called with type: {}".format(type(reports)))
        
        # Handle list containing a single dictionary
        if isinstance(reports, list) and len(reports) == 1 and isinstance(reports[0], dict):
            reports = reports[0]  # Extract the dictionary from the list
            logging.debug("Extracted dictionary from list")
        
        if isinstance(reports, dict):
            # Input is a dictionary with report numbers as keys
            report_numbers = list(reports.keys())
            reports_items = list(reports.items())
            logging.debug("Dict case - report_numbers: {}".format(report_numbers))
            logging.debug("Dict case - reports_items count: {}".format(len(reports_items)))
    
        # Ensure all report_numbers are strings
        report_numbers = [str(rn) for rn in report_numbers if rn is not None]
        logging.debug("Final report_numbers: {}".format(report_numbers))
        logging.debug("Final reports_items count: {}".format(len(reports_items)))
        
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
                logging.warning("Report {} not found in database".format(report_number))
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
            logging.error("Error processing report {}: {}".format(report_number, e))
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
                logging.info("Updated {} records in IMP_REPORT_LOG".format(len(updates_for_report_log)))
            except Exception as e:
                logging.error("Error updating IMP_REPORT_LOG: {}".format(e))
                raise
        
        # Insert into IMP_REPORT_STATUS_TRACKING
        if updates_for_status_tracking:
            try:
                self.cursor.executemany(SQL_QUERIES['INSERT_STATUS_TRACKING'], updates_for_status_tracking)
                logging.info("Inserted {} records in IMP_REPORT_STATUS_TRACKING".format(len(updates_for_status_tracking)))
            except Exception as e:
                logging.error("Error inserting into IMP_REPORT_STATUS_TRACKING: {}".format(e))
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
            
            logging.info("Starting bulk update for {} reports".format(len(reports)))
            logging.debug("Input reports type: {}".format(type(reports)))
            if isinstance(reports, dict):
                logging.debug("Report keys: {}".format(list(reports.keys())))
            
            # Step 1: Parse input and get existing reports
            report_numbers, reports_items = self._parse_reports_input(reports)
            logging.info("Parsed {} report numbers: {}...".format(len(report_numbers), report_numbers[:5]))  # Show first 5
            logging.info("Parsed {} report items".format(len(reports_items)))
            
            existing_reports = self._get_existing_reports_bulk(report_numbers)
            logging.info("Found {} existing reports in database".format(len(existing_reports)))


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
                logging.debug("Processing report {}".format(report_number))
                
                processed_report = self._process_single_report(
                    report_number, report_data, existing_reports
                )
                
                if processed_report is None:
                    missing_count += 1
                    logging.debug("Report {} not found in database or processing failed".format(report_number))
                    continue
                
                try:
                    # Prepare update data
                    report_log_update = self._prepare_report_log_update(processed_report)
                    status_tracking_insert = self._prepare_status_tracking_insert(processed_report)
                    
                    updates_for_report_log.append(report_log_update)
                    updates_for_status_tracking.append(status_tracking_insert)
                    
                    processed_count += 1
                    logging.debug("Successfully prepared updates for report {}".format(report_number))
                    
                except Exception as e:
                    failed_count += 1
                    logging.error("Error preparing updates for report {}: {}".format(report_number, e))
            
            logging.info("Processed {} reports, {} missing from DB, {} failed".format(processed_count, missing_count, failed_count))
            
            # Step 3: Execute bulk updates
            self._execute_bulk_updates(updates_for_report_log, updates_for_status_tracking)
            
            # Step 4: Commit the transaction
            self.connection.commit()
            logging.info("Database update completed successfully. Updated {} reports.".format(processed_count))
            return reports
            
        except Exception as e:
            # Rollback on error
            self.connection.rollback()
            logging.error("Database update failed: {}".format(e))
            raise


def update_db(connection, reports: Union[Dict, List]) -> str:
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

