set dotenv-filename := "secrets.docsy-dev.docker.env"

slack:
    poetry run python docsy/slack/slack.py

github:
    poetry run python docsy/github-bot/github-bot.py

api:
    poetry run python docsy/api/api.py

dashboard:
    poetry run python docsy/dashboard/dashboard.py

ngrok:
    ngrok http --domain reasonably-firm-cricket.ngrok-free.app 3000

cli:
    poetry run python docsy/cli/cli.py

# The format of the PEM key in the secrets file causes problems. Not sure where that comes from
docker_slack:
    docker build -t felixzieger/docsy .
    docker run -v=./data/:/app/data --env-file=./secrets.docsy-dev.docker.env -p 3000:3000 felixzieger/docsy
