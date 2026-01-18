import logging
import requests
import json
import os
import sys
import urllib3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from secure_password_store.password_manager import PasswordManager

# Disable SSL warnings if verify=False is used
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def load_config():
    """
    Load API configuration from unified config.ini file.
    
    Returns:
        dict: Configuration data (compatible with old api_config.json structure)
    """
    from utils.config_loader import get_api_config
    return get_api_config()


def login_and_get_session():
    """
    Logs into the specified API endpoint and returns an authenticated session object.
    This function sends a POST request to the login URL with the provided credentials
    and establishes a session if the login is successful. If the login fails or an
    exception occurs, it prints an error message and returns None.
    Returns:
        requests.Session: An authenticated session object if login is successful.
        None: If login fails or an exception occurs.
    """
    config = load_config()
    
    pm = PasswordManager()
    password = pm.get_password(config['credentials']['password_key'])
    logging.info('{} {}'.format(config["logging"]["info_messages"]["password_debug"], password))  # For debugging purposes, remove in production
    
    login_url = config['api']['base_url'] + config['api']['endpoints']['login']
    login_data = {
        'username': config['credentials']['username'],
        'password': password
    }
    session = requests.Session()
    
    # Configure SSL verification
    verify_ssl = True
    if 'ssl' in config and config['ssl']:
        verify_ssl = config['ssl'].get('verify_ssl', True)
        # Note: Python's requests library doesn't natively support JKS files.
        # The truststore_path is stored in config for reference, but SSL verification
        # will use Python's default certificate store or verify=False if disabled.
        if not verify_ssl:
            logging.warning("SSL verification is disabled. This is not recommended for production.")
    
    try:
        login_response = session.post(login_url, json=login_data, verify=verify_ssl)
        if login_response.status_code != config['http']['success_status_code']:
            error_msg = config['logging']['error_messages']['login_failed']
            logging.info('{} {}'.format(error_msg, login_response.text))
            session.close()
            return None
        logging.info(config['logging']['info_messages']['login_success'])
        return session
    except Exception as e:
        error_msg = config['logging']['error_messages']['login_failed']
        logging.error('{} {}'.format(error_msg, e))
        session.close()
        return None
    

def end_session(session):
    """
    End the current session by logging out and closing the session.
    
    Args:
        session: The requests Session object to end (can be None)
        
    Returns:
        bool: True if logout was successful, False otherwise
    """
    # Check if session exists
    if session is None:
        logging.debug("No session to close")
        return False
    
    config = load_config()
    logout_url = config['api']['base_url'] + config['api']['endpoints']['logout']
    success_code = config['http']['success_status_code']
    
    # Configure SSL verification (same as login)
    verify_ssl = True
    if 'ssl' in config and config['ssl']:
        verify_ssl = config['ssl'].get('verify_ssl', True)
    
    try:
        logout_response = session.post(logout_url, verify=verify_ssl)
        if logout_response.status_code == success_code:
            logging.info(config['logging']['info_messages']['logout_success'])
            session.close()
            return True
        else:
            error_msg = config['logging']['error_messages']['logout_failed']
            logging.error('{} {}'.format(error_msg, logout_response.text))
            session.close()
            return False
    except Exception as e:
        error_msg = config['logging']['error_messages']['logout_failed']
        logging.error('{} {}'.format(error_msg, e))
        try:
            session.close()
        except:
            pass  # Ignore errors when closing an already closed session
        return False

   
if __name__ == "__main__": 
    config = load_config()
    session = login_and_get_session()
    if session:
        print(config['main_messages']['session_success'])
        end_session(session)
    else:
        print(config['main_messages']['session_failed'])

        # /opt/xml-diagnose/api/api_session.py