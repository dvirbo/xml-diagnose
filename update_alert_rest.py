import requests
from zeep import Client
# Initialize the Zeep client with the WSDL URL
wsdl_url = 'http://localhost:8080/ActOne/services/alertsService?wsdl'
client = Client(wsdl=wsdl_url)
login_data = {
    'username': 'admin',
    'password': 'password'
}

req_url = 'http://localhost:8080/ActOne/api/public/v1/auth/login'
# Perform a POST request to the login endpoint
cache = 'http://localhost:8080/ActOne/api/v1/system/caches'
response = requests.delete(cache, json=login_data)

# Check if the login was successful
print('[DELETE] Cache Status Code:', response.status_code)
if response.status_code == 200:
    print('[DELETE] Cache cleared successfully!')
# response = requests.post(req_url, json=login_data)
# # Check if the login was successful 
# print('[POST] Login Status Code:', response.status_code)
# if response.status_code == 200:
#     print('[POST] Login successful!')
#     print('[POST] Response:', response.headers)
#     # Extract the COOKIE from the response
#     cookie = response.cookies.get_dict()
#     print('[POST] cookie:', cookie)
#     CSRFTOKEN = response.headers.get('CSRFTOKEN', None)
 
 
#     # Now you can use these cookies for subsequent requests
# else:
#     print('[POST] Login failed:', response.text)

# # chenage the cookie to a dictionary format 

# resource = 'http://localhost:8080/ActOne/actone/api/v1'
# # Make a GET request to the resource using the session cookies
# if cookie:
#     response = requests.get(resource, cookie)
#     print('[GET] Resource Status Code:', response.status_code)
#     if response.status_code == 200:
#         try:
#             file = open('output1.html', 'w', encoding='utf-8')
#             file.write(response.content.decode('utf-8') + '\n')
#             file.close()
#         except Exception as e:
#             print('[GET] Failed to write to file:', e)
#     else:
#         print('[GET] Failed to retrieve resource:', response.ok)
# else:
#     print('[GET] No valid cookies, skipping resource request.')