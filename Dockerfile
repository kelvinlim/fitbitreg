FROM python:3.11
WORKDIR /project

# environment needed for proxy server on ahc servers
#ENV HTTP_PROXY="http://ctsigate0.ahc.umn.edu:3128" 
#ENV HTTPS_PROXY="http://ctsigate0.ahc.umn.edu:3128"

# upgrade pip
RUN pip install --upgrade pip

COPY requirements.txt .

# install the necessary packages
RUN pip install -r requirements.txt

ADD . /project

# these are read from .env file using compose
ARG db_name
ARG db_dialect
ARG db_user
ARG db_pw
ARG db_port
ARG db_host

ARG CLIENT_ID
ARG CLIENT_SECRET
ARG REDIRECT_URI

ARG AUTHORIZATION_URL
ARG TOKEN_URL
ARG SECRET_KEY

CMD ["python","fitbit_flask.py"]

