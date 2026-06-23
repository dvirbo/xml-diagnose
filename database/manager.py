"""Database manager for handling database operations."""
import logging
from typing import List, Dict, Set, Tuple, Optional
from database.connection import connect_to_database
from database.updater import update_db
from database.queries import SQL_QUERIES


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
            result = [row[0] for row in rows]
            logging.info("Retrieved {} report_ids from latest process".format(len(result)))
            return result
        except Exception as e:
            logging.error("Error executing query to get reports from latest process: {}".format(e))
            return []

    def get_reports_to_process(self) -> Dict:
        """
        Get report IDs for XML filtering and no-response tracking.

        Returns:
            Dict with:
            - allowed_report_ids: latest process ∪ no-response reports (for XML filter)
            - no_response_ids: reports with no first/final response (for CSV placeholders)
            - report_metadata: {report_id: {alert_id, report_folder}} for no-response reports
        """
        empty = {
            'allowed_report_ids': set(),
            'no_response_ids': set(),
            'report_metadata': {},
        }
        if not self.connection:
            logging.error("No database connection available")
            return empty

        try:
            cursor = self.connection.cursor()
            cursor.execute(SQL_QUERIES['GET_REPORTS_FROM_LATEST_PROCESS'])
            latest_ids = [row[0] for row in cursor.fetchall()]

            cursor.execute(SQL_QUERIES['GET_REPORTS_NO_RESPONSE'])
            no_response_rows = cursor.fetchall()
            cursor.close()
        except Exception as e:
            logging.error("Error fetching reports to process: {}".format(e))
            return empty

        no_response_ids = set()
        report_metadata = {}
        for row in no_response_rows:
            report_id = row[0]
            no_response_ids.add(report_id)
            report_metadata[report_id] = {
                'alert_id': row[1] or '',
                'report_folder': row[2] or '',
            }

        latest_set = set(latest_ids)
        allowed_report_ids = latest_set | no_response_ids
        overlap = len(latest_set & no_response_ids)

        logging.info(
            "Report scope: {} from latest process, {} no-response, {} overlap, {} total".format(
                len(latest_set), len(no_response_ids), overlap, len(allowed_report_ids)
            )
        )
        return {
            'allowed_report_ids': allowed_report_ids,
            'no_response_ids': no_response_ids,
            'report_metadata': report_metadata,
        }
    
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
            result = {row[0] for row in rows}
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

