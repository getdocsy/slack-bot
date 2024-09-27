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
