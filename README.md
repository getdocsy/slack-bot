# docsy

Prior art:
https://github.com/humanloop/coworker

## Local Development

From the root of the project:
```
python docsy_slack.py
```

The app will listen on port 3000.

Start ngrok in a separate pane

```
ngrok http --domain reasonably-firm-cricket.ngrok-free.app 3000
```

Check ngrok enpoints https://dashboard.ngrok.com/cloud-edge/endpoints

### Create new database migration

From the root of the project:
```sh
poetry shell
alembic --config=docsy/alembic.ini revision --autogenerat -m "create base_branch column"
```

## Deployment using Docker

The app needs a persistent volume that is mapped to `/app/data/` within the container.

To run it locally `docker run -v=/Users/xilef/Documents/docsy/data/:/app/data --env-file=secrets.docsy-dev.docker.env -p 3000:3000 felixzieger/docsy`.

### Argument reference

GITHUB_APP_PRIVATE_KEY must be formatted without newlines
LOG_LEVEL can be one of DEBUG, INFO

