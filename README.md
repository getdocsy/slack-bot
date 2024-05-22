# should-this-be-in-the-docs-bot

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
ngrok http http://localhost:3000
```
