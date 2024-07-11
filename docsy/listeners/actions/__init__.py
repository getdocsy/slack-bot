from slack_bolt import App
from .sample_action import sample_action_callback
from docsy.github_manager import get_github_manager
import docsy.shared

ai = docsy.shared.ai
db = docsy.shared.db


def action_button_click_yes_callback(context, body, ack, say, client, channel_id):
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
    team_id = body["message"]["team"]
    gitHubManager = get_github_manager(db, team_id)
    file_paths = gitHubManager.list_md_files()
    file_path_suggestion = ai.get_file_path_suggestion(messages, file_paths)

    file_content = gitHubManager.get_file_content(file_path_suggestion)
    file_content_suggestion = ai.get_file_content_suggestion(
        messages, file_path_suggestion, file_content
    )

    branch_name_suggestion = ai.get_branch_name_suggestion(
        file_content, file_content_suggestion
    )

    gitHubManager.create_branch(
        branch_name=branch_name_suggestion,
    )
    gitHubManager.add_file(
        file_content=file_content_suggestion,
        relative_file_path=file_path_suggestion,
        commit_message=branch_name_suggestion,
    )
    gitHubManager.push_branch(
        branch_name=branch_name_suggestion,
    )
    organization_name = db.get_customer(team_id).organization_name
    html_url = gitHubManager.create_pr(
        branch_name_suggestion,
        branch_name_suggestion,
        f"I am Docsy. I am an AI coworker at {organization_name}. I created this PR based on a slack thread. Please merge or close as you see fit!",
    )

    url_block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"I opened a PR with that change. How does <{html_url}|this> look?",
        },
    }

    client.chat_postMessage(
        channel=channel_id,
        text="Placeholder",
        blocks=[url_block],
        thread_ts=thread_ts,
        token=context.bot_token,
    )


def action_button_click_no_callback(body, ack, say):
    ack()
    thread_ts = body["container"]["thread_ts"]
    say(
        f"All right, <@{body['user']['username']}>. No docs for this one.",
        thread_ts=thread_ts,
    )


def register(app: App):
    app.action("sample_action_id")(sample_action_callback)
    app.action("button_click_no")(action_button_click_no_callback)
    app.action("button_click_yes")(action_button_click_yes_callback)
