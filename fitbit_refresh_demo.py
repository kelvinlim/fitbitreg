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
import datetime
#from datetime import datetime, timedelta

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

    
"""
Define new method for accessing vo2max
"""
def get_vo2max(self,date):
    """
    Get the vo2max for specified day
    
    https://dev.fitbit.com/build/reference/web-api/cardio-fitness-score/get-vo2max-summary-by-date/
    
    /1/user/[user-id]/cardioscore/date/[date].json
    
    
    """
    
    url = "{0}/{1}/user/-/cardioscore/date/{year:04d}-{month:02d}-{day:02d}.json".format(
        *self._get_common_args(),
        year=date.year,
        month=date.month,
        day=date.day
    )
    return self.make_request(url)

def get_hrv_summary(self,date):
    """
    Get the vo2max for specified day
    
    https://dev.fitbit.com/build/reference/web-api/heartrate-variability/get-hrv-summary-by-date/
    
    /1/user/[user-id]/hrv/date/[date].json
    
    
    """
    
    url = "{0}/{1}/user/-/hrv/date/{year:04d}-{month:02d}-{day:02d}.json".format(
        *self._get_common_args(),
        year=date.year,
        month=date.month,
        day=date.day
    )
    return self.make_request(url)


def get_azm_summary(self,date, period='1d'):
    """
    Get the active zone minute for specified day
    
    https://dev.fitbit.com/build/reference/web-api/active-zone-minutes-timeseries/get-azm-timeseries-by-date/

    /1/user/[user-id]/activities/active-zone-minutes/date/[date]/[period].json
    
    """
    
    url = "{0}/{1}/user/-/activities/active-zone-minutes/date/{year:04d}-{month:02d}-{day:02d}/{period}.json".format(
        *self._get_common_args(),
        year=date.year,
        month=date.month,
        day=date.day,
        period=period
    )
    return self.make_request(url)


def get_hrv_intra(self, startDate, endDate=None):
    """
    Get the hrv intraday for  specified day or range if endDate is given
    

    /1/user/-/hrv/date/{startDate}/{endDate}.json

    /1/user/-/hrv/date/{date}/all.json
    
    """
    
    if endDate != None:
        # use startDate and endDate
        url = "{0}/{1}/user/-/activities/active-zone-minutes/date/{year:04d}-{month:02d}-{day:02d}/{year2:04d}-{month2:02d}-{day2:02d}/all.json".format(
            *self._get_common_args(),
            year=startDate.year,
            month=startDate.month,
            day=startDate.day,
            year2=endDate.year,
            month2=endDate.month,
            day2=endDate.day
        )
    
    else:
        # just use startDate   
        url = "{0}/{1}/user/-/hrv/date/{year:04d}-{month:02d}-{day:02d}/all.json".format(
            *self._get_common_args(),
            year=startDate.year,
            month=startDate.month,
            day=startDate.day
        )
    
    return self.make_request(url)
    
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

id = 221
row = db.get_fitbit_account(id)

client_info = {}
if row != None:
    client_info['id'] = id
    client_info['CLIENT_ID'] = row.userid
    client_info['CLIENT_SECRET'] = row.secret
    client_info['ACCESS_TOKEN'] = row.oauth_token
    client_info['REFRESH_TOKEN'] = row.fb_refresh_token

pass

# add new method to class
fitbit.Fitbit.get_vo2max = get_vo2max
fitbit.Fitbit.get_hrv_summary = get_hrv_summary
fitbit.Fitbit.get_azm_summary = get_azm_summary
fitbit.Fitbit.get_hrv_intra = get_hrv_intra

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
    fitbitData = {}
    fitbitData['dates'] = {}
    fitbitData['device'] = authd_client.get_devices()
    isoDate = '2024-05-03'
    
    # Set the start and end dates
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(weeks=3)

    # for isoDate in ['2024-05-01','2024-05-02','2024-05-03', '2024-05-04']:
    for isoDate in (start_date + datetime.timedelta(days=n) for n in range((end_date - start_date).days)):
        #dtObj = datetime.date.fromisoformat(isoDate.date())
        dtObj = isoDate.date()
        isoDateStr = dtObj.isoformat()
        
        print(isoDateStr)
        
        sleepData = authd_client.get_sleep(dtObj)
        # drop the minuteData
        # del sleepData['sleep'][0]['minuteData']
        
        # create dictionary for isoDateStr
        fitbitData['dates'][isoDateStr] = {}
        fitbitData['dates'][isoDateStr]['sleep'] = sleepData # sleepData['sleep'][0]
        fitbitData['dates'][isoDateStr].update(authd_client.get_vo2max(dtObj))
        fitbitData['dates'][isoDateStr].update(authd_client.get_hrv_summary(dtObj))
        fitbitData['dates'][isoDateStr].update(authd_client.get_azm_summary(dtObj))  
        #fitbitData['dates'][isoDate].update(authd_client.get_hrv_intra(dtObj))  
      
        # time series for steps
        # fitbitData.update(authd_client.time_series('activities/steps', user_id=None, base_date=isoDate,
        #                 period='1d',  # max, 7d 
        #                 end_date=None))
        
        # get different activities
        for resource in ['activityCalories','calories','caloriesBMR','distance','elevation','floors',\
                        'minutesSedentary','minutesLightlyActive','minutesFairlyActive','minutesVeryActive','steps']:
            fitbitData['dates'][isoDateStr].update(authd_client.time_series(f"activities/{resource}", user_id=None, base_date=isoDate,
                            period='1d',  # max, 7d 
                            end_date=None))    
            pass
        
        # save json to a file
        jsonfile = f"case_{id}_fitbit.json"
        with open(jsonfile, 'w') as fp:
            json.dump(fitbitData, fp, indent=4)
    
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
    exit(0)    

pass