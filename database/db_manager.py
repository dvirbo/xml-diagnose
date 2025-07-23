import logging
from typing import List, Dict


from database.db_usage import update_db
from database.establish_db import connect_to_database


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
    
    def update_reports(self, reports: List) -> List[Dict]:
        """Update database with reports and return summary"""
        if not self.connection:
            logging.error("No database connection available")
            return []
        
        summary_report = []
        
        if reports:
            logging.info(f"Updating database with {len(reports)} reports...")
            summary_report.extend(update_db(self.connection, reports))
        
        return summary_report
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed.")