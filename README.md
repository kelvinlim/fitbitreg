# fitbitreg

flask app for registration of fitbit user for sharing data

Note: be sure to end url with a /

e.g. https://lnpipapp2.med.umn.edu/fitbitrec/

## Need config info on dockerfile

```
sudo podman build -t fitbitreg .

sudo podman run -d -p 5000:5000 --restart unless-stopped fitbitreg

```

## Need info on setting up reverse proxy

nginx reverse proxy

```
        location /fitbitrec/ {
                proxy_pass http://127.0.0.1:5000;
                proxy_set_header Host $http_host;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-Proto $scheme;
                proxy_redirect http://$http_host/ https://$http_host/;
        }

```