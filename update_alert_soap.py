import requests
from zeep import Client
from zeep import Settings
from zeep.transports import Transport
import os


def login_and_get_session(login_url, login_data):
    """Authenticate and return a requests.Session with cookies set."""
    session = requests.Session()
    login_response = session.post(login_url, json=login_data)
    if login_response.status_code != 200:
        print('[ERROR] Login failed:', login_response.text)
        return None
    print('[INFO] Logged in successfully')
    return session

def create_zeep_client(wsdl_url, session): 
    """Create a Zeep SOAP client using the authenticated session."""
    transport = Transport(session=session, timeout=100)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=wsdl_url, transport=transport, settings=settings)
    return client

def get_alert_by_identifier(client, identifier):
    """Fetch alert data by identifier."""
    try:
        response = client.service.getAlertByIdentifier(identifier)
        with open('alert_response.xml', 'w', encoding='utf-8') as f:
            f.write(str(response))
        print('[SUCCESS] Response')
        return response
    except Exception as e:
        print('[ERROR] SOAP call failed:', e)
        return None

def prepare_updated_alert_data(alert_response, new_score='55'):
    """Prepare the alert data dictionary for update."""
    return {
        'alertAISCallXML': alert_response.alert.alertAISCallXML,
        'alertDate': alert_response.alert.alertDate,
        'alertIdentifier': alert_response.alert.alertIdentifier,
        'alertTypeIdentifier': alert_response.alert.alertTypeIdentifier,
        'alertTypeVersion': alert_response.alert.alertTypeVersion,
        'attributes': alert_response.alert.attributes,
        'buIdentifier': alert_response.alert.buIdentifier,
        'details': alert_response.alert.details,
        'ownerIdentifier': alert_response.alert.ownerIdentifier,
        'score': new_score,
        'statusIdentifier': alert_response.alert.statusIdentifier,
        'useZippedXml': alert_response.alert.useZippedXml,
        'xml': alert_response.alert.xml,
        'zippedXml': alert_response.alert.zippedXml
    }

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
        update_response = client.service.updateAlert(alertIdentifier=identifier, alert=updated_alert_data)
        print('[SUCCESS] Alert updated:', update_response)
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

def ActOne_login_and_get_session():
    login_url = 'http://localhost:8080/ActOne/api/public/v1/auth/login'
    login_data = {
        'username': 'admin',
        'password': 'password'
    }
    wsdl_url = os.path.join(os.path.dirname(__file__), 'alertsService.wsdl')

    # Step 1: Authenticate
    session = login_and_get_session(login_url, login_data)
    if not session:
        print('[ERROR] Failed to create session')
        return

    # Step 2: Create SOAP client
    client = create_zeep_client(wsdl_url, session)
    
    return client, session


def main():
    
    # updated_alert_data = prepare_updated_alert_data(response)
    # save_alert_data_to_file(updated_alert_data)

    # update_alert(client, identifier, updated_alert_data)

    # Step 6: close the session
    
    client, session = ActOne_login_and_get_session()
   # change_alert_status(client, ['SAM1-2025'], 'Inv In Process', force_status=False, additional_comments='testing status change')
    alert = get_alert_by_identifier(client, 'SAM1-2025')
    if alert:
        print(alert.alert.attributes[53])
        alert.attributes[53].value = '55'
        print(alert.alert.attributes[53])



        
    
    session.close()
if __name__ == "__main__":
    main()



    # __pydevd_ret_val_dict['get_alert_by_identifier'].alert.attributes[53]