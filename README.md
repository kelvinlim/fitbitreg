# fitbitreg

flask app for registration of fitbit user for sharing data

Note: be sure to end url with a /

e.g. https://lnpipapp2.med.umn.edu/fitbitrec/

## Need config info on dockerfile

```
sudo podman build -t fitbitreg .

sudo podman run -d -p 5010:5000 --restart unless-stopped fitbitreg

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

## for transferring a container

To copy an existing container from system a to system b (to get around the pip errors with hostname lookup on building containers on lnpitask-rh7.

1. Save

        podman save -o my_container.tar my_container_image

2. Transfer

        scp my_container.tar user@systemB:/path/to/destination

3. Load

        podman load -i /path/to/destination/my_container.tar
