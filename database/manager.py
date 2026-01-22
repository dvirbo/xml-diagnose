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
            query = SQL_QUERIES['GET_REPORTS_FROM_LATEST_PROCESS']
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            
            result = [row[0] for row in rows]
            logging.info("Retrieved {} report_ids from latest process".format(len(result)))
            return result
            
        except Exception as e:
            logging.error("Error executing query to get reports from latest process: {}".format(e))
            return []
    
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
        
        if reports:
            logging.info("Updating database with {} reports...".format(len(reports)))
            update_reports = update_db(self.connection, reports)
        
        return update_reports
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed.")

