import os
import logging

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from documentation_assistant import DocumentationAssistant
from github_manager import GitHubManager


logger = logging.getLogger(__name__)


app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
gitHubManager = GitHubManager("felixzieger/congenial-computing-machine","felixzieger",os.environ.get("GITHUB_TOKEN"))
ai = DocumentationAssistant()


@app.message("thanks")
def message_learned(message, say):
    thread_ts = message.get("thread_ts", None) or message["ts"]
    say(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hey there <@{message['user']}>! Looks like you learned something there. Should I create a PR against our public docs?",
                },
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Yes, please"},
                    "action_id": "button_click",
                },
            }
        ],
        text=f"Hey there <@{message['user']}>! Looks like you learned something there. Should I create a PR against our public docs?",
        thread_ts=thread_ts,
    )


@app.action("button_click")
def action_button_click(body, ack, say, client, channel_id):
    ack()
    thread_ts = body["container"]["thread_ts"]
    say(
        f"All right, <@{body['user']['username']}>. I'll get back to you with a suggestion",
        thread_ts=thread_ts,
    )

    thread = client.conversations_replies(channel=channel_id, ts=thread_ts).data[
        "messages"
    ]
    messages = [
        (message["user"], message["text"])
        for message in thread
        if "user" in message and "text" in message
    ]

    file_paths = gitHubManager.list_md_files()
    file_path_suggestion = ai.get_file_path_suggestion(messages, file_paths)

    logger.info(file_path_suggestion)

    file_content = gitHubManager.get_file_content(file_path_suggestion)
    file_content_suggestion = ai.get_file_content_suggestion(messages, file_path_suggestion, file_content)
    
    logger.info(file_content_suggestion)

    # gitHubManager.create_branch(file_content=file_content_suggestion, relative_file_path = file_path_suggestion)
    # html_url = gitHubManager.create_pr("My first end-to-end test")

    # url_block = {
    #     "type": "section",
    #     "text": {
    #         "type": "mrkdwn",
    #         "text": f"I opened a PR with that change. How does <{html_url}|this> look?",
    #     },
    # }

    # app.client.chat_postMessage(
    #     channel=channel_id, text="Placeholder", blocks=[url_block], thread_ts=thread_ts
    # )


@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


# Start your app
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
