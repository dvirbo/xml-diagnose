import logging
import requests

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from secure_password_store.password_manager import PasswordManager


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
    pm = PasswordManager()
    password = pm.get_password("ActOne")
    logging.info(f'[INFO] Using password: {password}')  # For debugging purposes, remove in production
    
    login_url = 'http://ifs-lab-2025:8080/ActOne/api/public/v1/auth/login'
    login_data = {
        'username': 'admin',
        'password': password
    }
    session = requests.Session()
    
    try:
        login_response = session.post(login_url, json=login_data)
        if login_response.status_code != 200:
            logging.info('[ERROR] Login failed:', login_response.text)
            session.close()
            return None
        logging.info('[INFO] Logged in successfully')
        return session
    except Exception as e:
        print('[ERROR] Login failed:', e)
        session.close()
        return None
    
if __name__ == "__main__":
    session = login_and_get_session()
    if session:
        print("Session established successfully.")
        session.close()
    else:
        print("Failed to establish session.")
    