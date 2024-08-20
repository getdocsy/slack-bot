import logging
import os
import requests
import difflib
import pprint
from docsy.github_manager import get_github_manager
import docsy.shared

logger = logging.getLogger(__name__)

ai = docsy.shared.ai
db = docsy.shared.db


# Downloads images and returns local file paths of the images
def download_images_from_thread(context, thread, team_id, thread_ts, base_file_name):
    download_folder = f"data/{team_id}/{thread_ts}/"  # TODO this folder must be cleaned up afterwards. Or use a temp folder
    logging.debug(
        f"Download images for thread {thread_ts} into folder {download_folder}"
    )
    image_paths = []
    for message in thread:
        if "files" in message:
            for file_info in message["files"]:
                if (
                    "mimetype" not in file_info
                    or "url_private_download" not in file_info
                ):
                    # without mimetype or download url, we can't decide if it's an image or download it
                    # so we skip it
                    continue

                if file_info["mimetype"].startswith("image/"):
                    file_url = file_info["url_private_download"]
                    # rename file to avoid naming conflicts
                    file_name = (
                        base_file_name
                        + "_"
                        + str(len(image_paths))
                        + "_"
                        + file_info["name"]
                    )
                    file_path = os.path.join(download_folder, file_name)

                    headers = {"Authorization": f"Bearer {context.bot_token}"}
                    response = requests.get(file_url, headers=headers)
                    if response.status_code == 200:
                        if not os.path.exists(download_folder):
                            os.makedirs(download_folder)
                        with open(file_path, "wb") as file:
                            file.write(response.content)
                        logging.debug(f"Downloaded {file_name} to {file_path}")
                        image_paths.append(file_path)
                    else:
                        logging.debug(f"Failed to download {file_name} from {file_url}")
    return image_paths


def action_button_click_yes_callback(context, body, ack, say, client, channel_id):
    ack()
    team_id = body["message"]["team"]
    channel_name = client.conversations_info(channel=channel_id)["channel"]["name"]
    username = body["user"]["username"]
    db.insert_event(
        {
            "title": "User accepts offer for PR creation",
            "description": f"User {username} accepts offer for PR creation in channel {channel_name}",
            "author": username,
            "team_id": team_id,
        }
    )
    thread_ts = body["container"]["thread_ts"]
    say(
        f"All right, <@{username}>. I'll get back to you with a suggestion",
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
    base_file_name = ai.get_base_file_name(messages)
    local_image_paths = download_images_from_thread(
        context, thread, team_id, thread_ts, base_file_name
    )

    try:
        gitHubManager = get_github_manager(db, team_id)

        file_paths = gitHubManager.list_md_files()
        file_path_suggestion = ai.get_file_path_suggestion(messages, file_paths)

        # Update sidebar if file is new and sidebar is configured
        if file_path_suggestion not in file_paths:
            sidebar_file_path = db.get_customer(team_id).sidebar_file_path
            if sidebar_file_path:
                sidebar_file_content = gitHubManager.get_file_content(sidebar_file_path)
                sidebar_content_suggestion = ai.get_sidebar_content_suggestion(
                    messages,
                    file_path_suggestion,
                    sidebar_file_content,
                )
                gitHubManager.add_file(
                    file_content=sidebar_content_suggestion,
                    relative_file_path=sidebar_file_path,
                )
            else:
                logging.info("No sidebar configured. Skipping sidebar update.")

            file_content = db.get_customer(team_id).front_matter or ""
        else:
            logging.info("File already exists. Skipping sidebar update.")
            file_content = gitHubManager.get_file_content(file_path_suggestion)

        file_content_suggestion = ai.get_file_content_suggestion(
            messages, local_image_paths, file_path_suggestion, file_content
        )
        assert file_content_suggestion is not None

        # Check if changes contain blacklisted words
        diff = difflib.unified_diff(
            file_content.splitlines(keepends=True),
            file_content_suggestion.splitlines(keepends=True),
        )
        blacklist = db.get_customer_blacklist(team_id)
        for line in diff:
            if line.startswith("+"):
                for word in blacklist:
                    if word in line:
                        say(
                            f"Sorry, I couldn't create the PR. The word '{word}' is blacklisted and appeared in the suggestion I created based on this thread."
                            + "This is a security measure to avoid leaking sensitive information to the public.",
                            thread_ts=thread_ts,
                        )
                        return

        branch_name_suggestion = ai.get_branch_name_suggestion(
            file_content, file_content_suggestion
        )

        gitHubManager.create_branch(  # TODO checking out an existing branch after having settled on content could lead to conflicts
            branch_name=branch_name_suggestion,
        )
        gitHubManager.add_file(
            file_content=file_content_suggestion,
            relative_file_path=file_path_suggestion,
        )

        for local_image_path in local_image_paths:
            # Only add image if it is referenced in answer
            if os.path.basename(local_image_path) in file_content_suggestion:
                gitHubManager.add_image(
                    local_image_path=local_image_path,
                )
        gitHubManager.commit(
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
    except Exception as e:
        logging.error(f"Failed to create PR. {e}")
        say(
            "Sorry, I couldn't create the PR.",
            thread_ts=thread_ts,
        )


def action_button_click_no_callback(body, ack, say, channel_id, client):
    ack()
    team_id = body["message"]["team"]
    channel_name = client.conversations_info(channel=channel_id)["channel"]["name"]
    username = body["user"]["username"]
    db.insert_event(
        {
            "title": "User declines offer for PR creation",
            "description": f"User {username} declines offer for PR creation in channel {channel_name}",
            "author": username,
            "team_id": team_id,
        }
    )
    thread_ts = body["container"]["thread_ts"]
    say(
        f"All right, <@{username}>. No docs for this one.",
        thread_ts=thread_ts,
    )
