#! /usr/bin/env python

from flask import Flask, render_template, url_for, redirect, send_file, request, Response
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from dotenv import dotenv_values
import json
import random
import string
import hashlib
import base64
import pkce

from werkzeug.middleware.proxy_fix import ProxyFix

# database code
from db_code import Db

# setup the db
db = Db()

version="0.5.0"
config = dotenv_values(".env")

# def generate_code_verifier(length: int) -> str:
#     rand = random.SystemRandom()
#     code_verifier = ''.join(rand.choices(string.ascii_letters + string.digits, k=length))
#     return code_verifier

# def generate_code_challenge(code_verifier: str) -> str:
#     code_sha_256 = hashlib.sha256(code_verifier.encode('utf-8')).digest()
#     code_challenge = base64.urlsafe_b64encode(code_sha_256).decode('utf-8')
#     return code_challenge

def generate_state(length: int) -> str:
    rand = random.SystemRandom()
    state = ''.join(rand.choices(string.ascii_letters + string.digits, k=length))
    return state

app = Flask(__name__)

# for dealing with reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

app.secret_key = config['SECRET_KEY']

# Flask-Bootstrap requires this line
Bootstrap(app)

class UserCodeForm(FlaskForm):
    usercode = StringField('Please enter the User Code provided by the study staff:', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
# Replace these with your Fitbit app credentials
CLIENT_ID = config['CLIENT_ID']
CLIENT_SECRET = config['CLIENT_SECRET']
REDIRECT_URI = config['REDIRECT_URI']
APP_PATH=config['APP_PATH']

# Fitbit URLs
AUTHORIZATION_URL = config['AUTHORIZATION_URL']
TOKEN_URL = config['TOKEN_URL']

# global variables
g_state = ''
g_code_verifier = ''
g_code_challenge = ''

@app.route(f"{APP_PATH}/", methods=['GET', 'POST'])
def index():
    
    global g_state, g_code_verifier, g_code_challenge

    form = UserCodeForm()
    message = ""
    if form.validate_on_submit():
        usercode = form.usercode.data
        id, register, wearable = db.entry_code_exists(usercode)
        if id and not register and wearable==2:
            # This is good entry code so get setup to go to fitbit site
            # the id exists and register=0
            # empty the form field
            form.usercode.data = ""
            
            # generate the three codes g_code_verifier, g_code_challenge, g_state
            g_code_verifier, g_code_challenge = pkce.generate_pkce_pair()
            g_state = generate_state(256)

            # save the g_state for this id in the uat so we can match it later to add the 
            # json_data and oauth_token
            db.update_fitbit_state(id, g_state)
            
            URL=AUTHORIZATION_URL + '?response_type=code' + \
                '&client_id=' + CLIENT_ID + \
                '&scope=activity+cardio_fitness+electrocardiogram+heartrate+location+nutrition+oxygen_saturation+profile+respiratory_rate+settings+sleep+social+temperature+weight' + \
                '&code_challenge=' + g_code_challenge + \
                '&code_challenge_method=S256' + \
                '&state=' + g_state + \
                '&redirect_url=' + REDIRECT_URI 
            
            # send to the fitbit site to authorize
            return redirect(URL)   
                        
            # oauth = OAuth1Session(client_key, client_secret=client_secret)
            # fetch_response = oauth.fetch_request_token(request_token_url, proxies=proxies)

            # resource_owner_key = fetch_response.get('oauth_token')
            # resource_owner_secret = fetch_response.get('oauth_token_secret')

            # #Save the oauth_token in the account with id
            # db.update_oauth_token_id(id, resource_owner_key)

            # if callback_uri:
            #     # use the callback_uri
            #     # how to use explicit callback: https://requests-oauthlib.readthedocs.io/en/latest/api.html?highlight=oauth_callback#requests_oauthlib.OAuth1Session.authorization_url
            #     authorization_url = oauth.authorization_url(base_authorization_url, 
            #     callback_uri=callback_uri)
            # else:
            #     # don't use callback_uri
            #     authorization_url = oauth.authorization_url(base_authorization_url)

            # return redirect(authorization_url,code=302)
        else:
            if id and register:
                message = f"usercode {usercode} exists but has already been registered."
            elif  id == 0:
                message = f"usercode {usercode} is not a valid code. Please recheck entry."
            elif wearable != 2:
                message = f"usercode {usercode} is not authorized for Fitbit. Please recheck entry."
            else:
                message = f"usercode {usercode} - there was an error, please check code"




    return render_template('index_usercode.html', form=form, message=message)


@app.route(f'{APP_PATH}/callback')
def callback():
    
    global g_state, g_code_verifier, g_code_challenge

    # Get authorization code from response
    code = request.args.get('code')
    state_returned = request.args.get('state')
    
    # does it match the state we sent?
    if g_state != state_returned:
        print(f"Error: no match on state {state_returned}")
    else:
        # Encode the client ID and secret for basic authentication
        credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
        headers = {
            'Authorization': f'Basic {base64.b64encode(credentials.encode()).decode()}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'client_id': CLIENT_ID,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'code': code,
            'code_verifier': g_code_verifier
        }
        response = requests.post(TOKEN_URL, data=data, headers=headers).json()
        access_token = response.get('access_token')
        
        # need to save the access information in the database, using the user_id?
        # also use the code to know what study
        db.update_fitbit_data(state_returned,
                              json_data = json.dumps(response),
                              fb_scope = response.get('scope'),
                              fb_refresh_token=response.get('refresh_token'),
                              oauth_token = access_token,
                              userid = response.get('user_id'),
                              register = 1
                              )
        return render_template("callback.html")


@app.route(f"{APP_PATH}/privacy")
def privacy():
   return render_template("privacy.html")

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5000)
    # app.run(debug=True,  host="0.0.0.0", port=5000)
