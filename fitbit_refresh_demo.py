#! /usr/bin/env python

"""
refresh token demo

https://python-fitbit.readthedocs.io/en/latest/

    
"""
from dotenv import dotenv_values
import fitbit

import requests
import base64
from pprint import pprint
import json

def refresh_access_token(client:dict ):
    
    """
    Refresh the access_token
    
    https://sl.bing.net/cyDruEhw0po
    
    """
    
    # Encode the credentials
    credentials = f"{client['CLIENT_ID']}:{client['CLIENT_SECRET']}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    # Set up the headers
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Set up the parameters
    params = {
        'grant_type': 'refresh_token',
        'refresh_token': client['REFRESH_TOKEN']
    }

    # Make the POST request
    response = requests.post('https://api.fitbit.com/oauth2/token', headers=headers, data=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the new access and refresh tokens
        new_tokens = response.json()
        access_token = new_tokens['access_token']
        refresh_token = new_tokens['refresh_token']
        # Use the new access token for subsequent API calls
        # save the data
        newData = {}
        newData['oauth_token'] = access_token
        newData['fb_refresh_token'] = refresh_token
        newData['fb_scope'] = new_tokens['scope']
        newData['json_data'] = json.dumps(response.json())
        
        # call db method
        db.update_fitbit_account(id, **newData) 
        pass
    else:
        # Handle errors
        print(f"Error refreshing token: {response.json()}")

    
    
# read the database

from db_code import Db

configdb = dotenv_values(".env")

config = dotenv_values(".env_kolim_data")

CLIENT_ID = config.get("CLIENT_ID")
CLIENT_SECRET = config.get("CLIENT_SECRET")
ACCESS_TOKEN = config.get("ACCESS_TOKEN")
REFRESH_TOKEN = config.get("REFRESH_TOKEN")


db = Db()


# let's retrieve the codes for a subject

"""
methods to use

get_fitbit_account(id)
update_fitbit_account(id, **kwargs)
"""

id = 223
row = db.get_fitbit_account(id)

client_info = {}
if row != None:
    client_info['id'] = id
    client_info['CLIENT_ID'] = row.userid
    client_info['CLIENT_SECRET'] = row.secret
    client_info['ACCESS_TOKEN'] = row.oauth_token
    client_info['REFRESH_TOKEN'] = row.fb_refresh_token

pass

# authorized

try:
    authd_client = fitbit.Fitbit(client_info.get('CLIENT_ID'),
                                client_info.get('CLIENT_SECRET'),
                                access_token=client_info.get('ACCESS_TOKEN'), 
                                refresh_token=client_info.get('REFRESH_TOKEN'))
    
except Exception as e:
    print(f"Error: {e}")
    exit(1)

try: 
    sleepData = authd_client.sleep(date='2024-03-2')
except Exception as e:
    print(f"Error: {e}")
    # check if Access token expired
    if "Access token expired" in str(e):
        # work on getting a new token and refreshing everything in database
        # need to use the fitbit app id and secret
        client_info['CLIENT_ID'] = configdb['CLIENT_ID']
        client_info['CLIENT_SECRET'] = configdb['CLIENT_SECRET']
        
        ddict = refresh_access_token(client_info)
        pass
    exit(1)    

pprint(sleepData)
pass