#! /usr/bin/env python

from flask import Flask, render_template, url_for, redirect, send_file, request, Response, session
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

# Define the version information
__version_info__ = ('1', '0', '2')
__version__ = '.'.join(__version_info__)

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

# Primary key of the Fitbit row in garmin_wearable (owned by garmin_django).
# Configured via .env so the magic number isn't buried in code.
FITBIT_WEARABLE_ID = int(config['FITBIT_WEARABLE_ID'])

@app.route(f"{APP_PATH}/", methods=['GET', 'POST'])
def index():

    form = UserCodeForm()
    message = ""
    version = __version__
    if form.validate_on_submit():
        usercode = form.usercode.data
        id, register, wearable = db.entry_code_exists(usercode)
        if id and not register and wearable == FITBIT_WEARABLE_ID:
            # This is good entry code so get setup to go to fitbit site
            # the id exists and register=0
            # empty the form field
            form.usercode.data = ""

            # PKCE verifier is stashed in the signed Flask session so it
            # survives the redirect to Fitbit and back without clobbering
            # other concurrent users (the previous module-global approach
            # broke under concurrency and didn't survive a restart).
            # `state` is still persisted to accounts.secret so the /callback
            # handler can look up which row to update from the returned state.
            code_verifier, code_challenge = pkce.generate_pkce_pair()
            state = generate_state(256)

            session['fb_code_verifier'] = code_verifier
            db.update_fitbit_state(id, state)

            URL=AUTHORIZATION_URL + '?response_type=code' + \
                '&client_id=' + CLIENT_ID + \
                '&scope=activity+cardio_fitness+electrocardiogram+heartrate+location+nutrition+oxygen_saturation+profile+respiratory_rate+settings+sleep+social+temperature+weight' + \
                '&code_challenge=' + code_challenge + \
                '&code_challenge_method=S256' + \
                '&state=' + state + \
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
            elif wearable != FITBIT_WEARABLE_ID:
                message = f"usercode {usercode} is not authorized for Fitbit. Please recheck entry."
            else:
                message = f"usercode {usercode} - there was an error, please check code"




    return render_template('index_usercode.html', form=form, message=message, version=version)


@app.route(f'{APP_PATH}/callback')
def callback():

    # Get authorization code from response
    code = request.args.get('code')
    state_returned = request.args.get('state')

    # The PKCE verifier was stashed in the user's signed session in index();
    # pop it so it isn't reused. If absent, the user never went through
    # index() in this browser (or the session expired) — reject.
    code_verifier = session.pop('fb_code_verifier', None)
    if code_verifier is None:
        print(f"Error: no code_verifier in session for state {state_returned}")
        return "Invalid session", 400
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
            'code_verifier': code_verifier
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
    app.run(debug=True, host="0.0.0.0", port=5010)  # production with container
    # app.run(debug=True, host="0.0.0.0", port=5000)  # production with container
    #app.run(debug=True,  host="127.0.0.1", port=5000)  # debugging
