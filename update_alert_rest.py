import logging
import requests
from typing import Dict, List, Any, Tuple
from login_and_get_session import login_and_get_session

logging.basicConfig(level=logging.INFO)


def process_alert(session: requests.Session, report: Dict[str, Any]) -> bool:
    """
    Process alert by updating custom fields based on report data.
    
    Args:
        session: HTTP session for making requests
        report: Dictionary containing alert data with keys: alert_id, mispar_tkina, status_divuah
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate required fields
        required_fields = ["report_id", "alert_id", "status_divuah", "mispar_tkina"]
        missing_fields = [field for field in required_fields if not report.get(field)]
        
        if missing_fields:
            logging.error(f"Missing required fields: {missing_fields}")
            return False
        
        # Extract data from report
        alert_id = report.get("alert_id")
        mispar_tkina = report.get("mispar_tkina")
        mispar_divuah = report.get("report_id")  
        status_divuah = report.get("status_divuah")
        
        # Fetch alert data
        url = f'http://ifs-lab-2025:8080/ActOne/api/v1/work-items/{alert_id}'
        logging.info(f"Fetching alert data for ID: {alert_id}")
        
        response = session.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch alert data. Status: {response.status_code}, Response: {response.text}")
            return False

        alert = response.json()
        
        # Update custom fields
        updated_alert, updated_fields = _update_custom_fields(alert, {
            "Mispar_tkina": mispar_tkina,
            "Mispar_divuah": mispar_divuah,
            "status_divuah": status_divuah
        })
        
        # Check if all expected fields were updated
        expected_field_count = 3
        if len(updated_fields) != expected_field_count:
            logging.warning(f"Expected to update {expected_field_count} fields, but only updated {len(updated_fields)}: {updated_fields}")
            return False
        
        logging.info(f"Successfully updated fields: {updated_fields}")
        
        # Update alert on server using PUT method
        update_url = f'http://ifs-lab-2025:8080/ActOne/api/v1/work-items/{alert_id}'
        headers = {'Content-Type': 'application/json'}
        
        response = session.post(update_url, json=updated_alert, headers=headers)
        if response.status_code not in [200, 204]:
            logging.error(f"Failed to update alert data. Status: {response.status_code}, Response: {response.text}")
            return False
        
        logging.info(f"Alert {alert_id} updated successfully")
        return True
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error occurred: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error in process_alert: {str(e)}")
        return False


def _update_custom_fields(alert: Dict[str, Any], field_updates: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Update custom fields in the alert object.
    
    Args:
        alert: Alert object containing customFields
        field_updates: Dictionary mapping field identifiers to new values
        
    Returns:
        tuple: (updated alert object, list of field identifiers that were successfully updated)
    """
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
            
            # Only update if value actually changed
            if old_value != new_value:
                field["value"] = new_value
                updated_fields.append(field_identifier)
                logging.info(f"Updated {field_identifier}: '{old_value}' -> '{new_value}'")
            else:
                logging.debug(f"Field {field_identifier} already has correct value: '{old_value}'")
                updated_fields.append(field_identifier)  # Still count as "updated" for validation
    
    return alert, updated_fields


def main() -> None:
    """Main function for testing the alert processing."""
    try:
        # Get session
        session = login_and_get_session()
        if not session:
            logging.error("Failed to get session")
            return
        
        # Example report data
        report_data = {
            "report_id": "12345",
            "alert_id": "SAM1-2210",
            "status_divuah": "תקין",
            "mispar_tkina": "122"
        }
        
        logging.info(f"Processing alert with data: {report_data}")
        success = process_alert(session, report_data)
        
        if success:
            logging.info("Alert processed successfully")
        else:
            logging.error("Failed to process alert")
            
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
    finally:
        if 'session' in locals() and session:
            session.close()


if __name__ == "__main__":
    main()