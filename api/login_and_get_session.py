import logging
import requests

logging.basicConfig(level=logging.INFO)

def login_and_get_session():
    """
    """
    login_url = 'http://ifs-lab-2025:8080/ActOne/api/public/v1/auth/login'
    login_data = {
        'username': 'admin',
        'password': 'password'
    }
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