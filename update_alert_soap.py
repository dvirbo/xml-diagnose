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


# Step 4: Update the alert with new data
updated_alert_data = {
    'alertAISCallXML': response.alert.alertAISCallXML,  # Use the existing AIS Call XML
    'alertDate':   response.alert.alertDate,  # Use the existing alert date
    'alertIdentifier': response.alert.alertIdentifier,  # Use the existing alert identifier
    'alertTypeIdentifier': response.alert.alertTypeIdentifier,  # Use the existing alert type identifier
    'alertTypeVersion': response.alert.alertTypeVersion,  # Use the existing alert type version
    'attributes': response.alert.attributes,  # Use the existing attributes
    'buIdentifier': response.alert.buIdentifier,  # Use the existing business unit identifier
    'details': response.alert.details,  # Use the existing details
    'ownerIdentifier': response.alert.ownerIdentifier,  # Use the existing owner identifier
    'score': '26',
    'statusIdentifier': response.alert.statusIdentifier,  # Use the existing status identifier
    'useZippedXml': response.alert.useZippedXml,  # Use the existing zipped XML flag
    'xml': response.alert.xml,  # Use the XML from the response
    'zippedXml': response.alert.zippedXml  # Use the existing zipped XML
} 

# test if the updated_alert_data is correct
# try:
#     with open('alert_data.xml', 'w', encoding='utf-8') as f:
#         f.write(str(updated_alert_data))
#         f.close()
#     print('[SUCCESS] Alert data prepared for update')
# except Exception as e:
#     print('[ERROR] Failed to prepare alert data:', e)

try:
    update_response = client.service.updateAlert(alertIdentifier=identifier, alert=updated_alert_data)
    print('[SUCCESS] Alert updated:', update_response)
except Exception as e:
    print('[ERROR] Failed to update alert:', e)