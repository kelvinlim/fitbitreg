# fitbitreg

flask app for registration of fitbit user for sharing data

Note: be sure to end url with a /

Production: deployed on `lnpitask0.med.umn.edu`, fronted by the local nginx on the same host. The container listens on 5010 and the app routes are mounted at `/` (APP_PATH is empty in `.env`); nginx strips the `/fitbitrec/` prefix when forwarding upstream.

## Build & run

```
sudo podman build -t fitbitreg .

sudo podman run -d --name fitbit -p 5010:5010 --restart unless-stopped fitbitreg
```

## nginx reverse proxy

The trailing slash on `proxy_pass` is what makes nginx strip the `/fitbitrec/` location prefix before forwarding to the container (which mounts at `/`).

```
        location /fitbitrec/ {
                proxy_pass http://10.88.0.1:5010/;
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

        podman save -o my_container.tar daae

2. Transfer

        scp my_container.tar kolim@lnpitask.ahc.umn.edu:

3. Load

        podman load -i my_container.tar
