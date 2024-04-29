FROM python:3.11
WORKDIR /app

# environment needed for proxy server on ahc servers
#ENV HTTP_PROXY="http://ctsigate0.ahc.umn.edu:3128" 
#ENV HTTPS_PROXY="http://ctsigate0.ahc.umn.edu:3128"

# upgrade pip
RUN pip install --upgrade pip

COPY requirements.txt .


# install the necessary packages
RUN pip install -r requirements.txt

COPY .env .

COPY . .

# ARG db_name=garmindb
# ARG db_dialect=mysql+pymysql
# ARG db_user=garminuser
# ARG db_pw="5bx82QkJ#n3p"
# ENV db_port=3306
# ARG db_host=lnpiapp.med.umn.edu
# ARG tz=US/Central

# ARG APP_PATH=/fitbitrec
# ARG CLIENT_ID=23RXNV
# ARG CLIENT_SECRET=65d2cb1761506b1d3d68300571af57a7
# ARG REDIRECT_URI=https://lnpiapp2.med.umn.edu/fitbitrec/callback

# ARG AUTHORIZATION_URL='https://www.fitbit.com/oauth2/authorize'
# ARG TOKEN_URL='https://api.fitbit.com/oauth2/token'
# ARG SECRET_KEY=top_secret_key_43fb04f9d7fc8ec5c58ebc8f564bcb4a

#CMD ["python","fitbit_flask.py"]
CMD ["/bin/bash"]