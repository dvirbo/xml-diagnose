import logging
import requests
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from secure_password_store.password_manager import PasswordManager


def load_config():
    """
    Load configuration from config.json file.
    
    Returns:
        dict: Configuration data
    """
    config_path = os.path.join(os.path.dirname(__file__), 'api_config.json')
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.error(f"[ERROR] Config file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"[ERROR] Invalid JSON in config file: {e}")
        raise


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
    logging.info(f'{config["logging"]["info_messages"]["password_debug"]} {password}')  # For debugging purposes, remove in production
    
    login_url = config['api']['base_url'] + config['api']['endpoints']['login']
    login_data = {
        'username': config['credentials']['username'],
        'password': password
    }
    session = requests.Session()
    
    try:
        login_response = session.post(login_url, json=login_data)
        if login_response.status_code != config['http']['success_status_code']:
            error_msg = config['logging']['error_messages']['login_failed']
            logging.info(f'{error_msg} {login_response.text}')
            session.close()
            return None
        logging.info(config['logging']['info_messages']['login_success'])
        return session
    except Exception as e:
        error_msg = config['logging']['error_messages']['login_failed']
        print(f'{error_msg} {e}')
        session.close()
        return None
    

def end_session(session):
    """
    End the current session by logging out and closing the session.
    
    Args:
        session: The requests Session object to end
        
    Returns:
        bool: True if logout was successful, False otherwise
    """
    config = load_config()
    logout_url = config['api']['base_url'] + config['api']['endpoints']['logout']
    success_code = config['http']['success_status_code']
    
    try:
        logout_response = session.post(logout_url)
        if logout_response.status_code == success_code:
            logging.info(config['logging']['info_messages']['logout_success'])
            session.close()
            return True
        else:
            error_msg = config['logging']['error_messages']['logout_failed']
            logging.error(f'{error_msg} {logout_response.text}')
            session.close()
            return False
    except Exception as e:
        error_msg = config['logging']['error_messages']['logout_failed']
        logging.error(f'{error_msg} {e}')
        session.close()
        return False

   
if __name__ == "__main__": 
    config = load_config()
    session = login_and_get_session()
    if session:
        print(config['main_messages']['session_success'])
        end_session(session)
    else:
        print(config['main_messages']['session_failed'])