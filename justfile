set dotenv-filename := "secrets.docsy-dev.docker.env"

slack_bot:
    @echo "Starting slack bot"
    poetry shell
    python docsy/slack_bot.py

github_bot:
    @echo "Starting github bot"
    poetry shell
    python docsy/github_bot.py


dashboard:
    @echo "Starting dashboard"
    poetry shell
    python docsy/slack_bot.py

ngrok:
    ngrok http --domain reasonably-firm-cricket.ngrok-free.app 3000

# The format of the PEM key in the secrets file causes problems. Not sure where that comes from
docker_slack_bot:
    docker build -t felixzieger/docsy .
    docker run -v=./data/:/app/data --env-file=./secrets.docsy-dev.docker.env -p 3000:3000 felixzieger/docsy
