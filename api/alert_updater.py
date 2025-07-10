import logging
from typing import List, Dict
from update_alert_rest import process_alert
from login_and_get_session import login_and_get_session

class AlertUpdater:
    """Handles alert updates via REST API"""
    
    def __init__(self):
        self.session = None
    
    def initialize_session(self) -> bool:
        """Create and validate session"""
        self.session = login_and_get_session()
        if not self.session:
            logging.error("Failed to create or validate session")
            return False
        
        logging.info("Session established successfully.")
        return True
    
    def update_alerts(self, summary_report: List[Dict]) -> bool:
        """Update alerts for all reports in summary"""
        if not self.session:
            logging.error("No valid session available")
            return False
        
        if not summary_report:
            logging.info("No reports to update")
            return True
        
        success_count = 0
        total_count = len(summary_report)
        
        logging.info(f"Updating {total_count} alerts...")
        
        for report in summary_report:
            update_status = process_alert(self.session, report)
            if update_status:
                success_count += 1
            else:
                logging.error(f"Failed to update alert for report: {report}")
        
        logging.info(f"Successfully updated {success_count}/{total_count} alerts")
        return success_count == total_count