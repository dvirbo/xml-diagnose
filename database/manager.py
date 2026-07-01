"""Database manager for handling database operations."""
import logging
from typing import List, Dict, Set, Tuple, Optional
from database.connection import connect_to_database
from database.updater import update_db
from database.queries import SQL_QUERIES


def _to_int_report_id(value) -> Optional[int]:
    """Normalize Oracle NUMBER/Decimal report_id to int."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class DatabaseManager:
    """Handles database operations"""
    
    def __init__(self):
        self.connection = None
    
    def connect(self) -> bool:
        """Establish database connection"""
        self.connection = connect_to_database()
        if self.connection:
            logging.info("Database connection established successfully.")
            return True
        else:
            logging.error("Failed to establish database connection.")
            return False
    
    def get_reports_from_latest_process(self) -> List[int]:
        """
        Execute query to get report_id values from the latest process.
        
        Returns:
            List of report_id values (integers)
            Returns empty list if query fails or no results
        """
        if not self.connection:
            logging.error("No database connection available")
            return []

        try:
            cursor = self.connection.cursor()
            cursor.execute(SQL_QUERIES['GET_REPORTS_FROM_LATEST_PROCESS'])
            rows = cursor.fetchall()
            cursor.close()
            result = [_to_int_report_id(row[0]) for row in rows]
            result = [rid for rid in result if rid is not None]
            logging.info("Retrieved {} report_ids from latest process".format(len(result)))
            return result
        except Exception as e:
            logging.error("Error executing query to get reports from latest process: {}".format(e))
            return []

    def _fetch_no_response_reports(self) -> Tuple[Set[int], Dict[int, Dict]]:
        """Query reports with no first/final response recorded in IMP_REPORT_LOG."""
        no_response_ids = set()
        report_metadata = {}
        if not self.connection:
            return no_response_ids, report_metadata

        try:
            cursor = self.connection.cursor()
            cursor.execute(SQL_QUERIES['GET_REPORTS_NO_RESPONSE'])
            rows = cursor.fetchall()
            cursor.close()
        except Exception as e:
            logging.error("Error fetching no-response reports: {}".format(e))
            return no_response_ids, report_metadata

        for row in rows:
            report_id = _to_int_report_id(row[0])
            if report_id is None:
                continue
            no_response_ids.add(report_id)
            report_metadata[report_id] = {
                'alert_id': row[1] or '',
                'report_folder': row[2] or '',
            }
        return no_response_ids, report_metadata

    def get_reports_no_response(self) -> Tuple[Set[int], Dict[int, Dict]]:
        """
        Reports still awaiting any Rashut response (both response fields NULL).
        Call after DB updates so CSV placeholders reflect current state.
        """
        no_response_ids, report_metadata = self._fetch_no_response_reports()
        logging.info(
            "Retrieved {} report_ids still awaiting Rashut response".format(len(no_response_ids))
        )
        return no_response_ids, report_metadata

    def get_reports_to_process(self) -> Dict:
        """
        Get report IDs for XML filtering and no-response tracking.

        Returns:
            Dict with:
            - allowed_report_ids: latest process ∪ no-response reports (for XML filter)
            - latest_process_ids: report IDs from the latest import process
            - no_response_ids: reports with no first/final response at query time (XML scope only)
            - report_metadata: metadata for no-response reports at query time
        """
        empty = {
            'allowed_report_ids': set(),
            'latest_process_ids': set(),
            'no_response_ids': set(),
            'report_metadata': {},
        }
        if not self.connection:
            logging.error("No database connection available")
            return empty

        try:
            cursor = self.connection.cursor()
            cursor.execute(SQL_QUERIES['GET_REPORTS_FROM_LATEST_PROCESS'])
            latest_ids = [_to_int_report_id(row[0]) for row in cursor.fetchall()]
            cursor.close()
        except Exception as e:
            logging.error("Error fetching reports to process: {}".format(e))
            return empty

        latest_set = {rid for rid in latest_ids if rid is not None}
        no_response_ids, report_metadata = self._fetch_no_response_reports()
        allowed_report_ids = latest_set | no_response_ids
        overlap = len(latest_set & no_response_ids)

        logging.info(
            "Report scope: {} from latest process, {} no-response, {} overlap, {} total".format(
                len(latest_set), len(no_response_ids), overlap, len(allowed_report_ids)
            )
        )
        return {
            'allowed_report_ids': allowed_report_ids,
            'latest_process_ids': latest_set,
            'no_response_ids': no_response_ids,
            'report_metadata': report_metadata,
        }

    def get_report_log_by_ids(self, report_ids: List[int]) -> List[Dict]:
        """Fetch IMP_REPORT_LOG rows for CSV export of answered reports."""
        if not self.connection or not report_ids:
            return []

        try:
            cursor = self.connection.cursor()
            placeholders = ','.join([':{}'.format(i + 1) for i in range(len(report_ids))])
            query = SQL_QUERIES['GET_REPORT_LOG_BY_IDS'].format(placeholders=placeholders)
            cursor.execute(query, report_ids)
            rows = cursor.fetchall()
            cursor.close()
        except Exception as e:
            logging.error("Error fetching report log by IDs: {}".format(e))
            return []

        result = []
        for row in rows:
            report_id = _to_int_report_id(row[0])
            if report_id is None:
                continue
            result.append({
                'report_id': report_id,
                'alert_id': row[1] or '',
                'sar_folder_name': row[2] or '',
                'first_response_orig': row[3],
                'final_response_valid': row[4],
                'status_desc': row[5] or '',
            })
        logging.info("Fetched {} IMP_REPORT_LOG rows for CSV export".format(len(result)))
        return result
    
    def get_report_numbers_by_ids(self, report_ids: List[int]) -> Set[int]:
        """
        Get report_numbers (report_ids) that exist in the database.
        This is used to filter which XML files to process.
        
        Args:
            report_ids: List of report_id values to check
            
        Returns:
            Set of report_id values that exist in the database
        """
        if not self.connection:
            logging.error("No database connection available")
            return set()
        
        if not report_ids:
            return set()
        
        try:
            cursor = self.connection.cursor()
            # Create placeholders for the IN clause
            placeholders = ','.join([':{}'.format(i+1) for i in range(len(report_ids))])
            query = SQL_QUERIES['GET_REPORT_NUMBERS_BY_IDS'].format(placeholders=placeholders)
            cursor.execute(query, report_ids)
            rows = cursor.fetchall()
            cursor.close()
            
            # Return set of report_ids that exist
            result = {_to_int_report_id(row[0]) for row in rows}
            result = {rid for rid in result if rid is not None}
            logging.info("Found {} report_ids in database out of {} requested".format(len(result), len(report_ids)))
            return result
            
        except Exception as e:
            logging.error("Error fetching report numbers by IDs: {}".format(e))
            return set()
    
    def update_reports(self, reports: List) -> List[Dict]:
            """Update database with reports and return summary"""
            if not self.connection:
                logging.error("No database connection available")
                return []
            
            if not reports:
                logging.info("No reports to update")
                return []
            
            logging.info("Updating database with {} reports...".format(len(reports)))
            update_reports = update_db(self.connection, reports)
            
            return update_reports
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed.")

