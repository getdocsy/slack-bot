from slack_bolt import App


def message_im_callback(message, say):
    user = message["user"]
    say(
        text=f"Hey there <@{user}>! Thanks for messaging"
    )


def register(app: App):
    app.message("")(message_im_callback)
