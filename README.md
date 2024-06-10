# docsy

Prior art:
https://github.com/humanloop/coworker

## Local Development

```
nix-shell

python docsy_slack.py
```

The app will listen on port 3000.

Start ngrok in a separate pane

```
ngrok http --domain reasonably-firm-cricket.ngrok-free.app 3000
```

## Deployment using Docker

The app needs a persistent volume that is mapped to `/app/data/` within the container.

To run it locally `docker run -v=/Users/xilef/Documents/docsy/data/:/app/data --env-file=secrets.docsy-dev.docker.env -p 3000:3000 felixzieger/docsy`.

### Argument reference

GITHUB_APP_PRIVATE_KEY must be formatted without newlines.

## Troubleshooting

Check ngrok enpoints https://dashboard.ngrok.com/cloud-edge/endpoints
