# fitbitreg

flask app for registration of fitbit user for sharing data


## Need config info on dockerfile

```
podman build -t fitbitreg .

podman run -d -p 5000:5000 --restart unless-stopped fitbitreg

```

## Need info on setting up reverse proxy

