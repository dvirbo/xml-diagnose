import logging
from api.update_alert_rest import process_alert
from api.api_session import login_and_get_session

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
    
    def update_alerts(self, reports: dict) -> bool:
        """Update alerts for all reports in summary"""
        if not self.session:
            logging.error("No valid session available")
            return False

        success_count = 0
        total_count = len(reports)

        for report_dict in reports:
            for report_number, report_data in report_dict.items():
            # Ensure report_number is also in the report data
            
                success = process_alert(self.session, report_data)
                if success:
                    success_count += 1
                    logging.info(
                        f"Report {report_number} processed successfully - "
                        f"Status: {report_data.get('Status', {}).get('status_category', 'N/A')}"
                    )
                else:
                    logging.error(f"Failed to process report {report_number}")

            logging.info(f"Completed processing {success_count} out of {total_count} reports successfully")
            return success_count == total_count

        
