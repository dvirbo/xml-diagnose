import logging
from typing import List, Dict
from api.update_alert_rest import process_alert
from api.login_and_get_session import login_and_get_session

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
    
    def update_alerts(self, summary_report: dict) -> bool:
        """Update alerts for all reports in summary"""
        if not self.session:
            logging.error("No valid session available")
            return False

        for report in summary_report:
            update_status = process_alert(self.session, report)
            if update_status:
                logging.info(f"Successfully updated alert for report: {report['report_number']} with status {report['status_divuah']} and mispar_tkina {report['mispar_tkina']}")
            else:
                logging.error(f"Failed to update alert for report: {report['report_number']}")
        
