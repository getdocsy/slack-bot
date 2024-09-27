import logging
import os
import base64
from openai import OpenAI

logger = logging.getLogger(__name__)

AI_MODEL = "gpt-4o-mini"


class AI:
    def __init__(self):
        self.client = OpenAI()
        self.base_prompt = [
            {
                "role": "system",
                "content": (
                    "You are Docsy, a friendly AI coworker. "
                    "Your help our company by improving our public documentation so it answers the questions people have about our product. "
                    "As input, you will receive chat conversations where someone asks a questions and someone answers the question. "
                ),
            },
        ]

    def _get_suggestion(self, prompt):
        logging.debug(prompt)
        completion = self.client.chat.completions.create(
            model=AI_MODEL, messages=prompt
        )
        suggestion = completion.choices[0].message.content
        logging.debug(suggestion)
        return suggestion

    def _convert_slack_thread_to_prompt(self, messages):
        return [
            {"role": "user", "name": message[0], "content": message[1]}
            for message in messages
        ]

    def _convert_images_to_prompt(self, image_paths):
        def _encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")

        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"This image was part of the chat conversation. It's available under assets/{os.path.basename(image_path)}. Reference it in the answer if it is relevant to the question.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{_encode_image(image_path)}",
                            "detail": "low",  # Expirement with this. Setting this to high might bring better results
                        },
                    },
                ],
            }
            for image_path in image_paths
        ]

    def get_base_file_name(self, messages):
        prompt = (
            self.base_prompt
            + self._convert_slack_thread_to_prompt(messages)
            + [
                {
                    "role": "user",
                    "content": (
                        "We need a prefix for images that appeared in this thread. This prefix will end up in the file name of the images. Please answer with exactly one suggestion, sticking to lowercase letters and hyphens."
                    ),
                },
            ]
        )
        return self._get_suggestion(prompt)

    def get_file_path_suggestion(self, messages, file_paths):
        prompt = (
            self.base_prompt
            + self._convert_slack_thread_to_prompt(messages)
            + [
                {
                    "role": "user",
                    "content": "Here is the list of files of the public documentation for our product.",
                },
            ]
            + [{"role": "user", "content": file_path} for file_path in file_paths]
            + [
                {
                    "role": "user",
                    "content": (
                        "Pick exactly one file path from the above list where you think the question from the chat conversation should be answered. Only answer with the file path. Include the complete path that was shown in the list. If no existing file is suitable, answer with a new file path."
                    ),
                },
            ]
        )
        return self._get_suggestion(prompt)

    def get_sidebar_content_suggestion(
        self, messages, new_file_path, sidebar_file_content
    ):
        prompt = (
            self.base_prompt
            + self._convert_slack_thread_to_prompt(messages)
            + [
                {
                    "role": "user",
                    "content": f"We want to answer this question in a new file {new_file_path} and need to add it to the sidebar. Please suggest a file path for the new file. Only answer with the file path. Stick to the format of the existing file paths.",
                },
                {
                    "role": "user",
                    "content": "Here is how the sidebar file currently looks like.",
                },
                {
                    "role": "user",
                    "content": sidebar_file_content,
                },
                {
                    "role": "user",
                    "content": (
                        "Now repeat the sidebar file line by line and only add a single line with the new file path where you think it fits best. It's very important that you do not leave out any lines that were there before."
                        + "We afterwards will open a Pull Request against the public docs and want only meaningful changes in our git history. Only answer with the new file content."
                        + "Do not add a codefence at the first line of the file."
                    ),
                },
            ]
        )
        return self._get_suggestion(prompt)

    def get_file_content_suggestion(
        self, messages, local_image_paths, file_path, file_content
    ):
        prompt = (
            self.base_prompt
            + self._convert_slack_thread_to_prompt(messages)
            + self._convert_images_to_prompt(local_image_paths)
            + [
                {
                    "role": "user",
                    "content": f"Please modify the file {file_path} to now also answer the question from the chat conversation above.",
                },
                {
                    "role": "user",
                    "content": "Here is how the file currently looks like.",
                },
                {
                    "role": "user",
                    "content": file_content,
                },
                {
                    "role": "user",
                    "content": (
                        "Now repeat the file line by line and only do the minimal edits necessary to answer the question. It's very important that you do not leave out any lines that were there before if not absolutely necesary."
                        + "We afterwards will open a Pull Request against the public docs and want only meaningful changes in our git history. Only answer with the new file content."
                        + "Do not add a codefence at the first line of the file."
                    ),
                },
            ]
        )
        return self._get_suggestion(prompt)

    def get_branch_name_suggestion(self, file_content, file_content_suggestion):
        prompt = self.base_prompt + [
            {
                "role": "user",
                "content": "Please suggest a branch name for the branch that will hold changes to the following file.",
            },
            {
                "role": "user",
                "content": "Here is how the file looked before the change.",
            },
            {
                "role": "user",
                "content": file_content,
            },
            {
                "role": "user",
                "content": "Here is how the file looks after the change.",
            },
            {
                "role": "user",
                "content": file_content_suggestion,
            },
            {
                "role": "user",
                "content": "Only answer with the suggested branch name. Only use lowercase letters and hyphens in the name. Keep the name short, if possible under 4 words.",
            },
        ]
        return self._get_suggestion(prompt)

    def get_next_action(self, messages, file_paths):
        prompt = (
            self.base_prompt
            + self._convert_slack_thread_to_prompt(messages)
            + [
                {
                    "role": "user",
                    "content": "Here is the list of files of the public documentation for our product.",
                }
            ]
            + [{"role": "user", "content": file_path} for file_path in file_paths]
            + [
                {
                    "role": "user",
                    "content": (
                        "Please decide what you want to do next. You can either answer free form or offer to create a pull request with what you were discussing in the conversation so far."
                        "Please only offer to create a PR if you are confident that the conversation contains enough information to create a meaningful PR."
                        "If you want to answer free form, please provide the answer in the next message."
                        "If you want to offer the creation of a pull request, please answer with SYSTEM_CREATE_PR"
                    ),
                },
            ]
        )
        return self._get_suggestion(prompt)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    ai = AI()
    messages = [
        ("Alice", "How do I activate my account?"),
        ("Bob", "Go to settings and click 'Activate Account'."),
    ]
    print(ai.get_file_path_suggestion(messages, ["README.md", "docs/account.md"]))
