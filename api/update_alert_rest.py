import logging
import requests
from typing import Dict, List, Any, Tuple
from api.api_session import login_and_get_session, load_config

logging.basicConfig(level=logging.INFO)


def process_alert(session: requests.Session, report: Dict[str, Any]) -> bool:
    """
    Processes an alert by fetching its data, updating custom fields, and sending the updated data back to the server.
    Args:
        session (requests.Session): The HTTP session to use for making API requests.
        report (Dict[str, Any]): A dictionary containing the report data. 
            Required keys include:
                - "report_id" (str): The ID of the report.
                - "alert_id" (str): The ID of the alert to be processed.
                - "status_divuah" (str): The status of the report.
                - "mispar_tkina" (str): The number that we getting from the Rashut after the report return with status "תקין"
    Returns:
        bool: True if the alert was successfully processed and updated, False otherwise.
    Raises:
        None: Any exceptions encountered during processing are logged and handled internally.
    Notes:
        - The function validates the presence of required fields in the `report` dictionary.
        - It fetches the alert data from the server using the `alert_id`.
        - Custom fields in the alert are updated based on the `report` data.
        - The updated alert is sent back to the server via a POST request.
        - Logs errors and warnings for missing fields, failed API requests, or partial updates.
    """
    
    try:
        # Validate required fields
        required_fields = ["report_id", "alert_id", "status_divuah", "mispar_tkina"]
        missing_fields = [field for field in required_fields if not report.get(field)]
        
        if missing_fields:
            logging.error(f"Missing required fields: {missing_fields}")
            return False

        config = load_config()
        base_url = config['api']['base_url']
        alert_id = report.get("alert_id")
        
        # Fetch alert data
        url = f'{base_url}/v1/work-items/{alert_id}'
        logging.info(f"Fetching alert data for ID: {alert_id}")
        
        response = session.get(url)
        if response.status_code != config['http']['success_status_code']:
            logging.error(f"Failed to fetch alert data. Status: {response.status_code}")
            logging.error(f"Error in alert id: {alert_id}")
            return False

        alert = response.json()
        
        # Update custom fields
        field_updates = {
            "Mispar_tkina": report.get("mispar_tkina"),
            "Mispar_divuah": report.get("report_id"),
            "status_divuah": report.get("status_divuah")
        }
        
        updated_alert, updated_fields = _update_custom_fields(alert, field_updates)
        
        # Validate all fields were updated
        if len(updated_fields) != len(field_updates):
            logging.warning(f"Expected {len(field_updates)} fields, updated {len(updated_fields)}")
            return False
        
        # Update alert on server
        headers = {'Content-Type': 'application/json'}
        response = session.post(url, json=updated_alert, headers=headers)
        
        if response.status_code not in [200, 204]:
            logging.error(f"Failed to update alert. Status: {response.status_code}")
            return False
        
        logging.info(f"Alert {alert_id} updated successfully")
        return True
            
    except Exception as e:
        logging.error(f"Error in process_alert: {str(e)}")
        return False


def _update_custom_fields(alert: Dict[str, Any], field_updates: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Update custom fields in the alert object."""
    updated_fields = []
    custom_fields = alert.get("customFields", [])
    
    if not custom_fields:
        logging.warning("No custom fields found in alert")
        return alert, updated_fields
    
    for field in custom_fields:
        field_identifier = field.get("identifier")
        if field_identifier in field_updates:
            old_value = field.get("value")
            new_value = field_updates[field_identifier]
            
            if old_value != new_value:
                field["value"] = new_value
                logging.info(f"Updated {field_identifier}: '{old_value}' -> '{new_value}'")
            
            updated_fields.append(field_identifier)
    
    return alert, updated_fields


def main() -> None:
    """Main function for testing the alert processing."""
    session = None
    try:
        session = login_and_get_session()
        if not session:
            logging.error("Failed to get session")
            return
        
        # Test data
        report_data = {
            "report_id": "12345",
            "alert_id": "SAM1-2210", 
            "status_divuah": "תקין",
            "mispar_tkina": "122"
        }
        
        success = process_alert(session, report_data)
        logging.info("Alert processed successfully" if success else "Failed to process alert")
            
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
    finally:
        if session:
            session.close()


if __name__ == "__main__":
    main()