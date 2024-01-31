# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn, params, options

# The Firebase Admin SDK to access Cloud Firestore.
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
import requests

#import functions_framework
#import os
#from dotenv import load_dotenv

import json

initialize_app()

'''
#load_dotenv()  # take environment variables from .env.
@functions_framework.http
def get_waiver_by_location(request):
    # Parse request to get variables
    if 'content-type' not in request.headers:
        return 'Invalid request'

    content_type = request.headers['content-type']

    if content_type == 'application/json':
        request_json = request.get_json(silent=True)

    if request_json and 'locationID' in request_json:
        locationID = request_json['locationID'].strip()
    if request_json and 'phone' in request_json:
        phone = request_json['phone'].strip()

        return json.dumps({'status': 'SUCCESS', 'phone': phone}), 200, {'ContentType':'application/json'} 

    else:
        return "ERROR: Missing Data"
'''


@https_fn.on_request(cors=options.CorsOptions(cors_origins="*", cors_methods=["post"]))
def get_waiver_by_location(req: https_fn.Request) -> https_fn.Response:
    location_key = req.get_json(silent=True)["locationID"] if "locationID" in req.get_json(silent=True) else None
    phone = req.get_json(silent=True)["phone"] if "phone" in req.get_json(silent=True) else None
    if ((location_key == None) or (phone == None)):
        https_fn.Response("Invalid Params", status=400)
    resp = __get_wavier_by_phone(location_key, phone)
    return https_fn.Response(json.dumps(resp.json()), status=200)


# [START get_wavier_by_phone]
CENTEREDGE_API_URL = params.SecretParam("CENTEREDGE_PROD_API_URL")

def __get_wavier_by_phone(location_key: str, phone: str) -> requests.Response:
    """Queries the centeredge api using phone as query param."""
    
    location_key = location_key.replace('-','').upper()
    loc_key_name = location_key+"_PROD_BUSINESS_ID"
    business_loc_id = params.SecretParam(loc_key_name).value
    loc_api_key = params.SecretParam(location_key+"_PROD_API_KEY").value
    
    headers = {"X-CE-ApplicationKey": f"{loc_api_key}"}
    url_params = {"skip": 0, "take": 100, "phoneNumber":phone}
    
    #/org/XXXX/waivers?skip=0&take=100&phoneNumber=1234567890' \
    
    url = CENTEREDGE_API_URL.value + f"/org/{business_loc_id}/waivers"
    
    return requests.get(url, params=url_params, headers=headers)

# [END get_wavier_by_phone]

