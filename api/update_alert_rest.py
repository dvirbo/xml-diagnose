import logging
import os
import sys
import requests
from typing import Dict, List, Any, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.api_session import load_config
from api.api_session import login_and_get_session

logging.basicConfig(level=logging.INFO)


def process_alert(session: requests.Session, report: Dict[str, Any]) -> bool:
    try:
        config = load_config()
        base_url = config["api"]["base_url"]
        alert_id = report['alert_id']

        url = f"{base_url}/v1/work-items/{alert_id}"
        logging.info(f"Fetching alert data for ID: {alert_id}")

        # Update alert on server with proper headers
        headers = {"accept": "*/*", "Content-Type": "application/json"}
        
        # Extract values from the report structure
        status_category = report.get('Status', {}).get('status_category', '')
        mispar_tkina = report.get('FinalResponse', {}).get('mispar_tkina', '')
        report_number = report.get('ReportNumber', '')

        # Prepare the data in the correct format
        payload = {
            "customFields": [
                {"identifier": "status_divuah", "value": status_category},
                {"identifier": "Mispar_tkina", "value": mispar_tkina},
                {"identifier": "Mispar_divuah", "value": report_number}
            ]
        }

        response = session.post(url, json=payload, headers=headers)

        if response.status_code not in [200, 204]:
            logging.error(f"Failed to update alert. Status: {response.status_code}")
            logging.error(f"Response content: {response.text}")
            return False

        logging.info(f"Alert {alert_id} updated successfully with status: {status_category}")
        return True

    except Exception as e:
        logging.error(f"Error in process_alert: {str(e)}")
        return False


def main() -> None:
    """Main function for testing the alert processing."""
    session = None
    try:
        session = login_and_get_session()
        if not session:
            logging.error("Failed to get session")
            return

        # Test data with proper structure
        report_data = {
            "customFields": [
                {"identifier": "status_divuah", "value": "valid"},
                {"identifier": "Mispar_tkina", "value": "112233"},
                {"identifier": "Mispar_divuah", "value": "112233"}
            ]
        }

        success = process_alert(session, report_data)
        logging.info(
            "Alert processed successfully" if success else "Failed to process alert"
        )

    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
    finally:
        if session:
            session.close()


if __name__ == "__main__":
    main()
