#! /usr/bin/env python

"""
refresh token demo

https://python-fitbit.readthedocs.io/en/latest/

    
"""
from dotenv import dotenv_values
import fitbit

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
id = 221
row = db.get_fitbit_account(id)

client_info = {}
if row != None:
    client_info['CLIENT_ID'] = row.userid
    client_info['CLIENT_SECRET'] = row.secret
    client_info['ACCESS_TOKEN'] = row.oauth_token
    client_info['REFRESH_TOKEN'] = row.ref

pass
"""
methods to use

get_fitbit_account(id)
update_fitbit_account(id, **kwargs)
"""
# authorized

try:
    authd_client = fitbit.Fitbit(CLIENT_ID,
                                CLIENT_SECRET,
                                access_token=ACCESS_TOKEN, 
                                refresh_token=REFRESH_TOKEN)
    
except Exception as e:
    print(f"Error: {e}")
    exit(1)

try: 
    sleepData = authd_client.sleep(date='2024-05-02')
except Exception as e:
    print(f"Error: {e}")
    exit(1)    

pass