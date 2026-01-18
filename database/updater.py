"""Database update operations."""
import cx_Oracle as oracledb
import logging
from typing import Dict, List, Tuple, Optional, Union
from database.queries import SQL_QUERIES, DB_SETTINGS
from database.connection import connect_to_alerts_database


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
        
        # first_response_valid: Convert boolean to CHAR(1) - 'Y'/'N' or '1'/'0'
        first_response_valid = status.get('first_response_valid', False)
        first_response_orig = 'Y' if first_response_valid else 'N'
        
        # final_response_valid: Convert boolean to CHAR(1) - 'Y'/'N' or '1'/'0'
        final_response_valid = status.get('final_response_valid', False)
        final_response_valid_char = 'Y' if final_response_valid else 'N'
        
        # Use ReportInstanceDate from FirstResponse for received_date
        # Convert string date to datetime object for Oracle DATE field
        received_date = None
        if first_response:
            date_str = first_response.get('ReportInstanceDate', '')
            if date_str:
                try:
                    from datetime import datetime
                    # Parse ISO format: 2025-01-02T01:25:55
                    received_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
                except (ValueError, TypeError) as e:
                    logging.warning("Could not parse ReportInstanceDate '{}': {}".format(date_str, e))
                    received_date = None
        
        # status_desc: Populated in code based on FIR and FIN response
        status_desc = status.get('status_category', '')
        
        # mispar_tkina: From FinalResponse/Mivzak/GeneralData/Statuses/Status[@id='']
        mispar_tkina = None
        if final_response and final_response_valid:
            mispar_tkina_str = final_response.get('mispar_tkina', '')
            if mispar_tkina_str:
                try:
                    mispar_tkina = int(mispar_tkina_str)
                except (ValueError, TypeError):
                    mispar_tkina = None
        
        return (
            first_response_orig,
            final_response_valid_char,
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
        from datetime import datetime
        
        first_response = processed_report.first_response
        final_response = processed_report.final_response
        status = processed_report.status
        
        # Update_date should be system date (current date/time)
        # Use datetime object instead of string for Oracle DATE field
        update_date = datetime.now()
        
        # tech_comment from ReportInstanceLegalStatusDesc (FIR)
        tech_comment = first_response.get('ReportInstanceLegalStatusDesc', '') if first_response else ''
        
        # business_comment from ReportInstanceLegalStatusDesc (FIN)
        business_comment = final_response.get('ReportInstanceLegalStatusDesc', '') if final_response else ''
        
        return (
            processed_report.report_id,
            processed_report.alert_id,
            update_date,
            tech_comment,
            business_comment
        )
    
    def _prepare_alert_update(self, processed_report: ProcessedReport) -> Optional[Tuple]:
        """
        Prepare data for UPDATE_ALERT query.
        
        Args:
            processed_report: ProcessedReport object
            
        Returns:
            Tuple of (p17, p18, p19, alert_id) or None if alert_id is missing
        """
        if not processed_report.alert_id:
            logging.warning("Alert update skipped for report {}: alert_id is missing".format(processed_report.report_number))
            return None
        
        status = processed_report.status
        final_response = processed_report.final_response
        
        # Log raw data for debugging
        logging.debug("Preparing alert update for report {}, alert_id {}".format(
            processed_report.report_number, processed_report.alert_id))
        logging.debug("Status data: {}".format(status))
        logging.debug("Final response data: {}".format(final_response))
        
        # p17 = status_divuah (status_category)
        p17 = status.get('status_category', '')
        logging.debug("p17 (status_category): '{}'".format(p17))
        
        # p18 = Mispar_tkina (from FinalResponse, as string for VARCHAR2(50))
        p18 = ''
        if final_response:
            mispar_tkina_raw = final_response.get('mispar_tkina', '')
            logging.debug("mispar_tkina from final_response: '{}' (type: {})".format(
                mispar_tkina_raw, type(mispar_tkina_raw).__name__))
            
            if mispar_tkina_raw:
                p18 = str(mispar_tkina_raw)
                logging.debug("p18 (Mispar_tkina) set to: '{}'".format(p18))
            else:
                logging.warning("mispar_tkina is empty or missing in final_response for report {}".format(
                    processed_report.report_number))
        else:
            logging.warning("Final response is None for report {}".format(processed_report.report_number))
        
        # p19 = Mispar_divuah (report_number without leading zeros)
        p19 = processed_report.report_number.lstrip('0') or '0'
        logging.debug("p19 (Mispar_divuah) from report_number '{}': '{}'".format(
            processed_report.report_number, p19))
        
        # Ensure all values are strings and max 50 chars for VARCHAR2(50)
        p17 = str(p17)[:50] if p17 else ''
        p18 = str(p18)[:50] if p18 else ''
        p19 = str(p19)[:50] if p19 else ''
        
        # Log final values being sent to database
        logging.info("Alert update prepared for alert_id {}: p17='{}', p18='{}', p19='{}'".format(
            processed_report.alert_id, p17, p18, p19))
        
        return (p17, p18, p19, processed_report.alert_id)

    def _execute_bulk_updates(self, updates_for_report_log: List[Tuple], 
                             updates_for_status_tracking: List[Tuple],
                             updates_for_alerts: List[Tuple] = None,
                             alerts_connection = None) -> None:
        """
        Execute bulk database updates.
        
        Args:
            updates_for_report_log: List of tuples for UPDATE_REPORT_LOG
            updates_for_status_tracking: List of tuples for INSERT_STATUS_TRACKING
            updates_for_alerts: List of tuples for UPDATE_ALERT
            alerts_connection: Connection to alerts database (optional)
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
        
        # Update ALERTS table (if alerts connection provided)
        # Note: Committed separately after main transaction (per requirement: same transaction conceptually, but different DB users)
        if updates_for_alerts and alerts_connection:
            try:
                # Log details of what we're about to update
                for idx, update_tuple in enumerate(updates_for_alerts[:5]):  # Log first 5 for debugging
                    logging.debug("Alert update #{}: p17='{}', p18='{}', p19='{}', alert_id='{}'".format(
                        idx + 1, update_tuple[0], update_tuple[1], update_tuple[2], update_tuple[3]))
                
                alerts_cursor = alerts_connection.cursor()
                alerts_cursor.executemany(SQL_QUERIES['UPDATE_ALERT'], updates_for_alerts)
                logging.info("Updated {} records in actone.alerts".format(len(updates_for_alerts)))
                
                # Log rowcount to verify updates
                logging.debug("Alert updates executed. Rows affected: {}".format(alerts_cursor.rowcount))
                
                # Note: Commit will be done after main connection commit
            except Exception as e:
                logging.error("Error updating actone.alerts: {}".format(e))
                import traceback
                logging.error("Traceback: {}".format(traceback.format_exc()))
                # Log warning and continue (per requirement - don't raise, just log)
                logging.warning("Continuing despite alert update errors")
                if alerts_connection:
                    try:
                        alerts_connection.rollback()
                    except:
                        pass
                # Don't raise - allow main transaction to proceed

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
            updates_for_alerts = []
            
            processed_count = 0
            missing_count = 0
            failed_count = 0
            
            # Connect to alerts database
            alerts_connection = None
            try:
                alerts_connection = connect_to_alerts_database()
                if not alerts_connection:
                    logging.warning("Failed to connect to alerts database. Alert updates will be skipped.")
            except Exception as e:
                logging.warning("Error connecting to alerts database: {}. Alert updates will be skipped.".format(e))
            
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
                    alert_update = self._prepare_alert_update(processed_report)
                    
                    updates_for_report_log.append(report_log_update)
                    updates_for_status_tracking.append(status_tracking_insert)
                    
                    if alert_update:
                        updates_for_alerts.append(alert_update)
                        # Log the actual values being added to batch
                        logging.debug("Added alert update to batch: p17='{}', p18='{}', p19='{}', alert_id='{}'".format(
                            alert_update[0], alert_update[1], alert_update[2], alert_update[3]))
                    else:
                        logging.warning("Skipping alert update for report {}: alert_id is missing".format(report_number))
                    
                    processed_count += 1
                    logging.debug("Successfully prepared updates for report {}".format(report_number))
                    
                except Exception as e:
                    failed_count += 1
                    logging.error("Error preparing updates for report {}: {}".format(report_number, e))
            
            logging.info("Processed {} reports, {} missing from DB, {} failed".format(processed_count, missing_count, failed_count))
            logging.info("Prepared {} alert updates".format(len(updates_for_alerts)))
            
            # Step 3: Execute bulk updates (including alerts if connection available)
            self._execute_bulk_updates(
                updates_for_report_log, 
                updates_for_status_tracking,
                updates_for_alerts if alerts_connection else None,
                alerts_connection
            )
            
            # Step 4: Commit the main transaction
            self.connection.commit()
            logging.info("Database update completed successfully. Updated {} reports.".format(processed_count))
            
            # Step 5: Commit alerts transaction (after main transaction succeeds)
            if alerts_connection and updates_for_alerts:
                try:
                    alerts_connection.commit()
                    logging.info("Alert updates committed successfully")
                except Exception as e:
                    logging.error("Failed to commit alerts transaction: {}".format(e))
                    # Continue anyway (per requirement)
                    try:
                        alerts_connection.rollback()
                    except:
                        pass
            
            # Close alerts connection if opened
            if alerts_connection:
                try:
                    alerts_connection.close()
                except Exception as e:
                    logging.warning("Error closing alerts connection: {}".format(e))
            
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

