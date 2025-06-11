import requests
from zeep import Client
from zeep.transports import Transport

# Step 1: Log in and get session cookies
login_url = 'http://localhost:8080/ActOne/api/public/v1/auth/login'
login_data = {
    'username': 'admin',
    'password': 'password'
}

session = requests.Session()
login_response = session.post(login_url, json=login_data)

if login_response.status_code != 200:
    print('[ERROR] Login failed:', login_response.text)
    exit()

print('[INFO] Logged in successfully')

# Step 2: Create Zeep client with the authenticated session
wsdl_url = 'http://localhost:8080/ActOne/services/alertsService?wsdl'
transport = Transport(session=session)
client = Client(wsdl=wsdl_url, transport=transport)
print(client.service)


# Step 3: Call the SOAP method with a valid identifier
identifier = 'SAM1-1856'  # replace with your actual alert ID
try:
    response = client.service.getAlertByIdentifier(identifier)
    with open('alert_response.xml', 'w', encoding='utf-8') as f:
        f.write(str(response))
        f.close()
    print('[SUCCESS] Response')
except Exception as e:
    print('[ERROR] SOAP call failed:', e)
# Step 4: Update the alert status
update_data = {
    'identifier': identifier,
    'status': 'CLOSED',  # or any other status you want to set
    'comment': 'Alert resolved successfully'
}


