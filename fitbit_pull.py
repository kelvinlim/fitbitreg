#! /usr/bin/env python

"""
Test pulling of data for a specific user account

https://python-fitbit.readthedocs.io/en/latest/

    
"""
from dotenv import dotenv_values
import fitbit



config = dotenv_values(".env_kolim_data")

CLIENT_ID = config.get("CLIENT_ID")
CLIENT_SECRET = config.get("CLIENT_SECRET")
ACCESS_TOKEN = config.get("ACCESS_TOKEN")
REFRESH_TOKEN = config.get("REFRESH_TOKEN")


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