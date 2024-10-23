# TODO: utilz go here 
"""

Docket & Dags - Charan
ETL Requests - Karthik 
Db connection and pulls - Yeshwanth
Ml flow + Darts - Eshwar 
Utils, config & panel - Richard
"""


## imports
import requests as r
import json
# microsoft Teams webhook Endpoint

urls="https://prod-121.westus.logic.azure.com:443/workflows/1c0a9b8fd8a14f6ab9c57724e7eeee0a/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=rNI0m0Kbp_2aWeDb11REvRtu-MlYaauI-rGMVV9i7ns"
# hit that endpoint with a post request

r.post(urls)

# Data to send to the webhook
data = {
    "text": "test"
}


url="https://prod-70.westus.logic.azure.com:443/workflows/ce842ad370aa4829b9bf882db9a1f5e2/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=x1iGF6uBixiFoTWgBNPFnY3RTbwsdq7AK9x9ueNwt_Y"

# Define the message you want to send
message = {
    "text": "test"
}

# Send the message
response = r.post(
    url, 
    data=json.dumps(message),
    headers={'Content-Type': 'application/json'}
)


# Send the POST request
response = r.post(urls, json=data)
response.status_code

response.raise_for_status()
# discord webhook endpoint

url="https://discord.com/api/webhooks/1298490100736458844/AdBPy6LBJyrrZ6tTkA2sZMsdgZXEbrWudgi6QuTtd7wTJ6plscpWtVBGSqCaFXX8lVFT"

# hit that endpoint with a post request

r.post(whurls)

