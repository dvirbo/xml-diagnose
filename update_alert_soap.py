import requests
from zeep import Client
from zeep import Settings
from zeep.transports import Transport
import os


def login_and_get_session(login_url, login_data):
    """Authenticate and return a requests.Session with cookies set."""
    session = requests.Session()
    try:
        login_response = session.post(login_url, json=login_data)
        if login_response.status_code != 200:
            print('[ERROR] Login failed:', login_response.text)
            session.close()  # Close session on failure
            return None
        print('[INFO] Logged in successfully')
        return session
    except Exception as e:
        print('[ERROR] Login failed:', e)
        session.close()  # Ensure session is closed on exception
        return None

def create_zeep_client(wsdl_url, session): 
    """Create a Zeep SOAP client using the authenticated session."""
    # Ensure cookies and headers are passed to the Transport object
    transport = Transport(session=session, timeout=1000)
    settings = Settings(strict=False, xml_huge_tree=True)  
    client = Client(wsdl=wsdl_url, transport=transport, settings=settings)
    return client

def get_alert_by_identifier(client, identifier):
    """Fetch alert data by identifier."""
    try:
        response = client.service.getAlertByIdentifier(identifier)
        file_name = f'alert_{identifier}.xml'
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(str(response))
        print('[SUCCESS] Response')
        return response
    except Exception as e:
        print('[ERROR] SOAP call failed:', e)
        return None

def prepare_updated_alert_data(alert_response):
    """Prepare the alert data dictionary for update.""" 
    # Ensure all mandatory fields are included and properly formatted
    updated_data = {
        'alertAISCallXML': alert_response.alert.alertAISCallXML or '',
        'alertDate': alert_response.alert.alertDate,
        'alertIdentifier': alert_response.alert.alertIdentifier,
        'alertTypeIdentifier': alert_response.alert.alertTypeIdentifier,
        'alertTypeVersion': alert_response.alert.alertTypeVersion,
        'attributes': alert_response.alert.attributes,
        'buIdentifier': alert_response.alert.buIdentifier,
        'details': alert_response.alert.details,
        'ownerIdentifier': alert_response.alert.ownerIdentifier,
        'score': 23,  # Example updated score
        'statusIdentifier': alert_response.alert.statusIdentifier,
        'useZippedXml': alert_response.alert.useZippedXml,
        'xml': alert_response.alert.xml,
        'zippedXml': alert_response.alert.zippedXml
    }
    return updated_data

def save_alert_data_to_file(alert_data, filename='alert_data.xml'):
    """Save alert data to a file for inspection."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(alert_data))
        print('[SUCCESS] Alert data prepared for update')
    except Exception as e:
        print('[ERROR] Failed to prepare alert data:', e)

def update_alert(client, identifier, updated_alert_data):
    """Update the alert using the SOAP service."""
    try:
        update_response = client.service.updateAlert(
            alertIdentifier=identifier, 
            alert=updated_alert_data
        )
        if update_response and update_response.alertResult:
            print('[INFO] AlertResult:', update_response.alertResult)
        return update_response
    except Exception as e:
        print('[ERROR] Failed to update alert:', e)
        return None

def change_alert_status(client, alert_identifiers, status_identifier, force_status=False, additional_comments="", alert_result_list=None):
    """
    Change the status of one or more alerts using the SOAP service.
    """
    try:
        response = client.service.changeAlertStatus(
            alertsIdentifiers=alert_identifiers,
            statusIdentifier=status_identifier,
            forceStatus=force_status,
            additionalComments=additional_comments,
            alertResultList=alert_result_list
        )
        print('[SUCCESS] Alert status changed:', response)
        return response
    except Exception as e:
        print('[ERROR] Failed to change alert status:', e)
        return None
    


def add_notes_request(client, alert_identifier, notes, is_confidential=False):
    """
    Add notes to an alert using the SOAP service.

    :param client: Zeep client instance
    :param alert_identifier: The alert identifier (string)
    :param notes: List of note strings to add
    :param is_confidential: Boolean flag for confidentiality
    :return: SOAP response
    """
    try:
        response = client.service.addNotes(
            alertIdentifier=alert_identifier,
            notes=notes,
            isConfidential=is_confidential
        )
        print('[SUCCESS] Notes added:', response)
        return response
    except Exception as e:
        print('[ERROR] Failed to add notes:', e)
        return None

def validate_session(session):
    """Validate the session by checking cookies and headers."""
    if not session.cookies or not session.headers:
        print('[ERROR] Session is invalid or expired.')
        return False
    print('[INFO] Session is valid.')
    return True

def ActOne_login_and_get_session():
    login_url = 'http://localhost:8080/ActOne/api/public/v1/auth/login'
    login_data = {
        'username': 'admin',
        'password': 'password'
    }
    wsdl_url = 'http://localhost:8080/ActOne/services/alertsService?wsdl'

    # Step 1: Authenticate
    session = login_and_get_session(login_url, login_data)
    if not session or not validate_session(session):
        print('[ERROR] Failed to create or validate session')
        return None, None

    # Step 2: Create SOAP client
    client = create_zeep_client(wsdl_url, session)
    return client, session

def main():
    
    alert_id = 'SAM1-2199'
    client, session = ActOne_login_and_get_session()
    if not client or not session:
        print("[ERROR] Failed to initialize client or session")
        return

    try:
        alert = get_alert_by_identifier(client, alert_id)
        if alert and 'alert' in alert and 'attributes' in alert['alert']:
            # Find and update the specific attribute
            attribute_found = False
            for attr in alert['alert']['attributes']:
                if attr['identifier'] == 'Mispar_divuah':  # Note: case-sensitive match
                    attr['value'] = '241098'  # Update the 'value' field, not the entire attributes list
                    attribute_found = True
                    print(f"[INFO] Updated Mispar_divuah to: {attr['value']}")
                    break
            
            if not attribute_found:
                print("[WARNING] Attribute 'Mispar_divuah' not found in alert")
        else:
            print("[ERROR] Alert or attributes not found.")
            return
        
        # Prepare updated alert data
        updated_alert_data = prepare_updated_alert_data(alert)
        
        # Update the alert
        update_response = update_alert(client, alert_id, updated_alert_data)
        if update_response and update_response.alertResult:
            print('[SUCCESS] Alert updated')
        else:
            print('[ERROR] Alert update failed')
    except Exception as e:
        print('[ERROR] An error occurred:', e)
    finally:
        session.close()  # Ensure session is closed in all cases
        print("[INFO] Session closed")

if __name__ == "__main__":
  main()






