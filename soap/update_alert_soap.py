import requests
import requests_cache
from zeep import Client, Settings
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin
import logging

logging.basicConfig(level=logging.INFO)

def login_and_get_session(login_url, login_data):
    """
    Authenticate to a given URL using provided login data and return a configured requests.Session.
    Args:
        login_url (str): The URL endpoint to send the login request to.
        login_data (dict): The login credentials or payload to be sent in the request body.
    Returns:
        requests.Session or None: A requests.Session object with authentication cookies and headers set if login is successful, otherwise None.
    Notes:
        - If the login response contains a JSON Web Token (JWT) in the 'token' field, it will be added to the session headers as a Bearer token.
        - Prints error messages if login fails or if the response cannot be parsed as JSON.
    """
    session = requests.Session()
    try:
        login_response = session.post(login_url, json=login_data)
        if login_response.status_code != 200:
            print('[ERROR] Login failed:', login_response.text)
            session.close()
            return None
        logging.info('[INFO] Logged in successfully')
        return session
    except Exception as e:
        print('[ERROR] Login failed:', e)
        session.close()
        return None



def create_zeep_client(wsdl_url, auth_session):
    """
    Creates and returns a Zeep SOAP client with WSDL caching and authentication.
    This function sets up a Zeep client for SOAP web services, using a cached session
    for WSDL retrieval to improve performance. It copies cookies and headers from the
    provided authenticated session, and optionally sets the Authorization header for
    SOAP requests if present. The client is configured with relaxed XML parsing and
    a history plugin for debugging.
    Args:
        wsdl_url (str): The URL to the WSDL file describing the SOAP service.
        auth_session (requests.Session): An authenticated requests session containing
            necessary cookies and headers for authentication.
    Returns:
        zeep.Client: A configured Zeep SOAP client ready for making service calls.
    """
    # Cache WSDL only — not SOAP calls
    wsdl_session = requests_cache.CachedSession(
        cache_name='zeep_wsdl_cache',
        backend='sqlite',
        expire_after=3600
    )
    wsdl_session.cookies.update(auth_session.cookies)
    wsdl_session.headers.update(auth_session.headers)

    transport = Transport(session=wsdl_session, timeout=1000)
    settings = Settings(strict=False, xml_huge_tree=True)
    history = HistoryPlugin()

    client = Client(wsdl=wsdl_url, transport=transport, settings=settings, plugins=[history])

    # Copy cookies from the authenticated session to the Zeep client
    # This is necessary for maintaining the session state
    if 'Authorization' in auth_session.headers:
        auth_header = auth_session.headers['Authorization']
        client.transport.session.headers['Authorization'] = auth_header

    return client



def validate_session(session):
    """Basic validation of session cookies and headers."""
    if not session.cookies or not session.headers:
        print('[ERROR] Session is invalid or expired.')
        return False
    print('[INFO] Session is valid.')
    return True


def ActOne_login_and_get_session():
    login_url = 'http://ifs-lab-2025:8080/ActOne/api/public/v1/auth/login'
    login_data = {
        'username': 'admin',
        'password': 'password'
    }
    wsdl_url = 'http://ifs-lab-2025:8080/ActOne/services/alertsService?wsdl'

    session = login_and_get_session(login_url, login_data)
    if not session or not validate_session(session):
        print('[ERROR] Failed to create or validate session')
        return None, None

    client = create_zeep_client(wsdl_url, session)
    return client, session


def get_alert_by_identifier(client, identifier):
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


def save_alert_data_to_file(alert_data, filename='alert_data.xml'):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(alert_data))
        print('[SUCCESS] Alert data prepared for update')
    except Exception as e:
        print('[ERROR] Failed to prepare alert data:', e)


def main():
    """
    Main function to update the status of a specific alert in the system.
    This function performs the following steps:
    1. Logs in to the ActOne system and initializes a client and session.
    2. Retrieves an alert by its identifier.
    3. Searches for the attribute 'status_divuah' within the alert's attributes.
        - If found, updates its value to 'DONE'.
        - If not found, logs a warning.
    4. Updates the alert in the system with the modified attributes.
    5. Handles errors and exceptions during the process.
    6. Ensures the session is closed after execution.
    Returns:
         None
    """
    alert_id = 'SAM1-2206'
    client, session = ActOne_login_and_get_session()
    if not client or not session:
        logging.error("[ERROR] Failed to initialize client or session")
        return

    try:
        alert = get_alert_by_identifier(client, alert_id)
        if alert and 'alert' in alert and 'attributes' in alert['alert']:
            attribute_found = False
            for attr in alert['alert']['attributes']:
                if attr['identifier'] == 'status_divuah':
                    attr['value'] = 'DONE'
                    attribute_found = True
                    logging.info('Updated status_divuah to: %s', attr['value'])
                    break

            if not attribute_found:
                logging.warning("Attribute 'status_divuah' not found in alert")
        else:
            logging.error("Alert or attributes not found.")
            return

        # update_response = update_alert(client, alert_id, alert['alert'])
        # if update_response and update_response.alertResult:
        #     logging.info('Alert updated successfully')
        # else:
        #     logging.error('Alert update failed')
    except Exception as e:
        logging.error('An error occurred: %s', e)
    finally:
        session.close()
        logging.info("Session closed")
        
def rest_test():
    login_url = 'http://ifs-lab-2025:8080/ActOne/api/public/v1/auth/login'
    login_data = {
        'username': 'admin',
        'password': 'password'
    }
    session = login_and_get_session(login_url, login_data)
    if not session or not validate_session(session):
        print('[ERROR] Failed to create or validate session')
        return None
    
    
    url = 'http://ifs-lab-2025:8080/ActOne/api/v1/work-items/SAM1-2205'
    try:
        # Use the authenticated session directly (no second login)
        response = session.get(url)
        if response.status_code != 200:
            print(f'[ERROR] Request failed with status {response.status_code}:', response.text)
            return None
        print('[SUCCESS] REST API call successful')
        alert = response.json()
        
        
        
    except Exception as e:
        print('[ERROR] An error occurred during the request:', e)
        return None
    finally:
        session.close()

if __name__ == "__main__":
    main()
    
   # rest_test()
    


